# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLoan(models.Model):
    _name = 'hr.loan.fx'
    _description = 'Employee Loan (Foreign Currency)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string='المرجع', required=True, copy=False, default='New', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, tracking=True)
    contract_id = fields.Many2one(
        'hr.contract', string='العقد',
        domain="[('employee_id', '=', employee_id)]")
    company_id = fields.Many2one(
        'res.company', string='الشركة', default=lambda self: self.env.company, required=True)

    # عملة القرض (مثال: USD) وعملة الشركة (مثال: SDG) - مستقلتان عن بعض
    currency_id = fields.Many2one(
        'res.currency', string='عملة القرض', required=True, tracking=True,
        default=lambda self: self.env.company.currency_id)
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', string='عملة الشركة', store=True)

    loan_amount = fields.Monetary(
        string='مبلغ القرض', currency_field='currency_id', required=True, tracking=True)
    number_of_installments = fields.Integer(string='عدد الأقساط', required=True, default=1)
    installment_amount = fields.Monetary(
        string='قيمة القسط (بعملة القرض)', currency_field='currency_id',
        compute='_compute_installment_amount', store=True)
    date_start = fields.Date(
        string='تاريخ أول استقطاع', required=True, default=fields.Date.context_today)

    # الحسابات المحاسبية المستخدمة عند القسط (لازم تكون فيها Secondary Currency = عملة القرض)
    loan_account_id = fields.Many2one(
        'account.account', string='حساب القرض (رصيد الموظف)', required=True,
        help='يجب أن يكون لهذا الحساب "Secondary Currency" مضبوطة على عملة القرض حتى'
             ' يتم حفظ amount_currency تلقائيًا في القيود.')

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معتمد'),
        ('running', 'قيد السداد'),
        ('done', 'مكتمل'),
        ('cancel', 'ملغي'),
    ], default='draft', tracking=True, string='الحالة')

    loan_line_ids = fields.One2many('hr.loan.fx.line', 'loan_id', string='الأقساط')

    total_paid_currency = fields.Monetary(
        string='المسدد (بعملة القرض)', currency_field='currency_id', compute='_compute_totals')
    balance_currency = fields.Monetary(
        string='الرصيد المتبقي (بعملة القرض)', currency_field='currency_id',
        compute='_compute_totals')

    @api.depends('loan_amount', 'number_of_installments')
    def _compute_installment_amount(self):
        for loan in self:
            loan.installment_amount = (
                loan.loan_amount / loan.number_of_installments
                if loan.number_of_installments else 0.0
            )

    @api.depends('loan_line_ids.paid', 'loan_line_ids.amount_currency')
    def _compute_totals(self):
        for loan in self:
            paid_lines = loan.loan_line_ids.filtered('paid')
            loan.total_paid_currency = sum(paid_lines.mapped('amount_currency'))
            loan.balance_currency = loan.loan_amount - loan.total_paid_currency

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan.fx') or 'New'
        return super().create(vals_list)

    def action_approve(self):
        for loan in self:
            if loan.state != 'draft':
                raise UserError(_('يمكن اعتماد القروض في حالة المسودة فقط.'))
            if loan.currency_id == loan.company_currency_id:
                raise UserError(_(
                    'عملة القرض هي نفسها عملة الشركة، لا حاجة لآلية العملة الأجنبية هنا.'))
            loan._generate_installment_lines()
            loan.state = 'approved'

    def action_set_running(self):
        self.write({'state': 'running'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def _generate_installment_lines(self):
        self.ensure_one()
        self.loan_line_ids.unlink()
        remaining = self.loan_amount
        amount = self.installment_amount
        lines = []
        for i in range(self.number_of_installments):
            installment = remaining if i == self.number_of_installments - 1 else amount
            remaining -= installment
            due_date = fields.Date.add(self.date_start, months=i)
            lines.append((0, 0, {
                'name': _('قسط %s') % (i + 1),
                'sequence': i + 1,
                'due_date': due_date,
                'amount_currency': installment,
            }))
        self.loan_line_ids = lines

    def get_due_installment(self, date_from, date_to):
        """يرجع أول قسط مستحق وغير مسدد ضمن فترة الراتب المعطاة."""
        self.ensure_one()
        return self.loan_line_ids.filtered(
            lambda l: not l.paid and date_from <= l.due_date <= date_to
        )[:1]


class HrLoanLine(models.Model):
    _name = 'hr.loan.fx.line'
    _description = 'قسط القرض'
    _order = 'sequence, id'

    loan_id = fields.Many2one('hr.loan.fx', string='القرض', required=True, ondelete='cascade')
    employee_id = fields.Many2one(related='loan_id.employee_id', store=True, string='الموظف')
    currency_id = fields.Many2one(related='loan_id.currency_id', store=True, string='عملة القرض')
    company_currency_id = fields.Many2one(
        related='loan_id.company_currency_id', store=True, string='عملة الشركة')

    name = fields.Char(string='الوصف', required=True)
    sequence = fields.Integer(default=10)
    due_date = fields.Date(string='تاريخ الاستحقاق', required=True)

    amount_currency = fields.Monetary(
        string='المبلغ (بعملة القرض)', currency_field='currency_id')
    amount_company_currency = fields.Monetary(
        string='المبلغ (بعملة الشركة وقت الاستقطاع)',
        currency_field='company_currency_id', readonly=True)
    exchange_rate = fields.Float(string='سعر الصرف المستخدم', digits=(16, 6), readonly=True)

    paid = fields.Boolean(string='مسدد', default=False, readonly=True)
    payslip_id = fields.Many2one('hr.payslip', string='قسيمة الراتب', readonly=True)

    def mark_paid(self, payslip, amount_company_currency, exchange_rate):
        self.write({
            'paid': True,
            'payslip_id': payslip.id,
            'amount_company_currency': amount_company_currency,
            'exchange_rate': exchange_rate,
        })
