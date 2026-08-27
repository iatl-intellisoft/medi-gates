# -*- coding: utf-8 -*-
import calendar

from odoo import api, fields, models, _
from odoo.exceptions import UserError

MONTH_SELECTION = [
    ('01', 'January'), ('02', 'February'), ('03', 'March'),
    ('04', 'April'), ('05', 'May'), ('06', 'June'),
    ('07', 'July'), ('08', 'August'), ('09', 'September'),
    ('10', 'October'), ('11', 'November'), ('12', 'December'),
]

STATE_SELECTION = [
    ('draft', 'Draft'),
    ('sales_review', 'Sales Review'),
    ('accounting_review', 'Accounting Review'),
    ('approved', 'Approved'),
    ('done', 'Done'),
]


class SalesAppraisal(models.Model):
    _name = 'sales.appraisal'
    _description = 'Sales Monthly Appraisal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, month desc, salesperson_id'

    name = fields.Char(string='Reference', copy=False, readonly=True,
                        default=lambda self: _('New'))
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', tracking=True,
        help="Optional link to the HR employee record.")
    salesperson_id = fields.Many2one(
        'res.users', string='Salesperson', required=True, tracking=True,
        domain=[('share', '=', False)],
        states={'done': [('readonly', True)]})
    month = fields.Selection(MONTH_SELECTION, string='Month', required=True,
                              tracking=True,
                              default=lambda self: '%02d' % fields.Date.today().month)
    year = fields.Integer(string='Year', required=True, tracking=True,
                           default=lambda self: fields.Date.today().year)
    date_from = fields.Date(string='Period Start', compute='_compute_period',
                             store=True)
    date_to = fields.Date(string='Period End', compute='_compute_period',
                           store=True)
    state = fields.Selection(STATE_SELECTION, string='Status', default='draft',
                              tracking=True, copy=False, required=True)

    kpi_line_ids = fields.One2many(
        'sales.appraisal.kpi', 'appraisal_id', string='KPI Lines',
        copy=True)

    kpi_line_quantitative_ids = fields.One2many(
        'sales.appraisal.kpi', 'appraisal_id', string='Quantitative KPIs',
        domain=[('category_id.code', '=', 'quantitative')])
    kpi_line_administrative_ids = fields.One2many(
        'sales.appraisal.kpi', 'appraisal_id', string='Administrative KPIs',
        domain=[('category_id.code', '=', 'administrative')])
    kpi_line_guarantee_collection_ids = fields.One2many(
        'sales.appraisal.kpi', 'appraisal_id', string='Guarantee Collection KPIs',
        domain=[('category_id.code', '=', 'guarantee_collection')])
    kpi_line_deduction_ids = fields.One2many(
        'sales.appraisal.kpi', 'appraisal_id', string='Deduction KPIs',
        domain=[('category_id.code', '=', 'deduction')])

    max_total_rate = fields.Float(
        string='Max Total Rate (%)', digits=(6, 4), default=2.0,
        help="Overall cap applied to the sum of all KPI rates.")
    total_kpi_rate = fields.Float(
        string='Total KPI Rate (%)', digits=(6, 4),
        compute='_compute_total_kpi_rate', store=True)
    final_rate = fields.Float(
        string='Final Rate (%)', digits=(6, 4),
        compute='_compute_total_kpi_rate', store=True,
        help="MIN(Total KPI Rate, Max Total Rate)") 
    total_amount_collected_by_kpi = fields.Monetary(string='Total Amount Collected By KPI', compute='_compute_total_amount_collected_by_kpi')
    total_amount_collected_on_time_by_kpi = fields.Monetary(string='Total Amount Collected Time By KPI',compute='_compute_total_amount_collected_on_time_by_kpi')
    on_time_kpi_rate = fields.Float(string='On Time KPI Rate', default=0.5)

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)

    total_collected = fields.Monetary(
        string='Total Collected', compute='_compute_total_collected',
        store=True, help="Sum of reconciled customer payments for this "
                          "salesperson's invoices within the period "
                          "(on-time + late).")
    total_amount_incentive = fields.Monetary(
            string='Total Amount Incentive', compute='_compute_total_amount_incentive',
            store=True)
    total_collected_on_time = fields.Monetary(
            string='Collected On Time', compute='_compute_total_collected',
            store=True, help="Payments made on or before the related invoice's "
                              "due date.")
    total_collected_late = fields.Monetary(
        string='Collected Late', compute='_compute_total_collected',
        store=True, help="Payments made after the related invoice's due "
                          "date (overdue collections).")
    payout_amount = fields.Monetary(
        string='Payout Amount', compute='_compute_payout_amount', store=True,
        help="Total Collected x Final Rate")

    target_id = fields.Many2one(
        'sales.appraisal.target', string='Collection Target',
        compute='_compute_target_id', store=True, readonly=True)
    collection_target = fields.Monetary(
        related='target_id.collection_target', string='Target', store=True)
    achievement_percent = fields.Float(
        string='Achievement (%)', compute='_compute_achievement', store=True,
        digits=(6, 2))

    can_edit_sales = fields.Boolean(
        string='Can Edit Sales KPIs', compute='_compute_can_edit')
    can_edit_accounting = fields.Boolean(
        string='Can Edit Accounting KPIs', compute='_compute_can_edit')

    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('appraisal_uniq', 'unique(salesperson_id, month, year, company_id)',
         'An appraisal already exists for this salesperson and period.'),
    ]

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends('month', 'year')
    def _compute_period(self):
        for rec in self:
            if rec.month and rec.year:
                month = int(rec.month)
                last_day = calendar.monthrange(rec.year, month)[1]
                rec.date_from = fields.Date.to_date('%s-%s-01' % (rec.year, rec.month))
                rec.date_to = fields.Date.to_date(
                    '%s-%s-%02d' % (rec.year, rec.month, last_day))
            else:
                rec.date_from = False
                rec.date_to = False

    @api.depends('kpi_line_ids.rate', 'max_total_rate')
    def _compute_total_kpi_rate(self):
        for rec in self:
            total = sum(rec.kpi_line_ids.mapped('rate'))
            rec.total_kpi_rate = total
            rec.final_rate = min(total, rec.max_total_rate) if rec.max_total_rate else total

    @api.depends('salesperson_id', 'date_from', 'date_to', 'company_id')
    def _compute_total_collected(self):
        AccountPayment = self.env['account.payment']
        for rec in self:
            if not (rec.salesperson_id and rec.date_from and rec.date_to):
                rec.total_collected = 0.0
                rec.total_collected_on_time = 0.0
                rec.total_collected_late = 0.0
                continue
            payments = AccountPayment.search([
                ('state', '=', 'paid'),
                ('payment_type', '=', 'inbound'),
                ('partner_type', '=', 'customer'),
                ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to),
                ('company_id', '=', rec.company_id.id),
            ])
            total = 0.0
            total_on_time = 0.0
            total_late = 0.0
            for payment in payments:
                invoices = payment.reconciled_invoice_ids.filtered(
                    lambda inv: inv.invoice_user_id.id == rec.salesperson_id.id)
                if not invoices:
                    continue
                # NOTE (MVP simplification): if a single payment settles
                # invoices from several salespeople, its full amount is
                # counted here rather than being split proportionally.
                # For an exact split, compute matched amounts via
                # account.partial.reconcile instead.
                total += payment.amount

                # On-time vs late: compare the payment date against the
                # earliest due date among the matched invoices. If the
                # payment was made on or before that due date, it is
                # considered "on time"; otherwise it is "late".
                due_dates = invoices.mapped('invoice_date_due')
                due_dates = [d for d in due_dates if d]
                if due_dates and payment.date and payment.date <= min(due_dates):
                    total_on_time += payment.amount
                else:
                    # No due date on the invoice(s), or paid after due date
                    total_late += payment.amount

            rec.total_collected = total
            rec.total_collected_on_time = total_on_time
            rec.total_collected_late = total_late

    @api.depends('total_collected', 'final_rate')
    def _compute_payout_amount(self):
        for rec in self:
            rec.payout_amount = rec.total_collected * (rec.final_rate or 0.0) / 100.0 

    @api.depends('total_amount_collected_on_time_by_kpi','total_amount_collected_by_kpi')
    def _compute_total_amount_incentive(self):
        for rec in self:
            if rec.total_amount_collected_on_time_by_kpi and rec.total_amount_collected_by_kpi :
                rec.total_amount_incentive = rec.total_amount_collected_on_time_by_kpi + rec.total_amount_collected_by_kpi
    

    @api.depends('total_collected_on_time')
    def _compute_total_amount_collected_on_time_by_kpi(self):
        for rec in self:
            rec.total_amount_collected_on_time_by_kpi = rec.total_collected_on_time * rec.on_time_kpi_rate

    @api.depends('total_collected','total_kpi_rate')
    def _compute_total_amount_collected_by_kpi(self):
        for rec in self:
            rec.total_amount_collected_by_kpi = rec.total_collected * rec.total_kpi_rate

    @api.depends('salesperson_id', 'month', 'year', 'company_id')
    def _compute_target_id(self):
        Target = self.env['sales.appraisal.target']
        for rec in self:
            rec.target_id = False
            if rec.salesperson_id and rec.month and rec.year:
                target = Target.search([
                    ('salesperson_id', '=', rec.salesperson_id.id),
                    ('month', '=', rec.month),
                    ('year', '=', rec.year),
                    ('company_id', '=', rec.company_id.id),
                ], limit=1)
                rec.target_id = target.id if target else False

    @api.depends('total_collected', 'collection_target')
    def _compute_achievement(self):
        for rec in self:
            if rec.collection_target:
                rec.achievement_percent = (rec.total_collected / rec.collection_target) * 100.0
            else:
                rec.achievement_percent = 0.0

    def _compute_can_edit(self):
        is_accounting = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_accounting')
        is_sales = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_sales')
        is_manager = self.env.user.has_group(
            'sales_monthly_appraisal.group_appraisal_manager')
        for rec in self:
            rec.can_edit_sales = is_manager or (
                is_sales and rec.state in ('draft', 'sales_review'))
            rec.can_edit_accounting = is_manager or (
                is_accounting and rec.state == 'accounting_review')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sales.appraisal') or _('New')
        records = super().create(vals_list)
        records._sync_kpi_lines()
        return records

    def _sync_kpi_lines(self):
        """Create one KPI line per active KPI definition that is not
        already present on the appraisal."""
        Line = self.env['sales.appraisal.kpi']
        for rec in self:
            existing_defs = rec.kpi_line_ids.mapped('kpi_definition_id')
            definitions = self.env['sales.appraisal.kpi.definition'].search([
                ('active', '=', True),
                ('id', 'not in', existing_defs.ids),
            ])
            for definition in definitions:
                Line.create({
                    'appraisal_id': rec.id,
                    'kpi_definition_id': definition.id,
                })

    # ------------------------------------------------------------------
    # Workflow actions
    # ------------------------------------------------------------------
    def action_submit_sales_review(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft appraisals can be submitted for Sales Review."))
        self.write({'state': 'sales_review'})

    def action_submit_accounting_review(self):
        for rec in self:
            if rec.state != 'sales_review':
                raise UserError(_("Only appraisals in Sales Review can move to Accounting Review."))
        self.write({'state': 'accounting_review'})

    def action_approve(self):
        for rec in self:
            if rec.state != 'accounting_review':
                raise UserError(_("Only appraisals in Accounting Review can be approved."))
        self.write({'state': 'approved'})
    def action_done(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Only approved appraisals can be marked as Done."))
        self.write({'state': 'done'})
        self.env['sales.appraisal.incentive'].create({
                    'salesperson_id': self.salesperson_id.id,
                    # 'employee_id': self.employee_id.id if self.employee_id else False,
                    'year':self.year,
                    'month': self.month,
                    'total_amount_collected': self.total_collected,
                    'total_amount_collected_by_kpi': self.total_amount_collected_by_kpi,
                    'total_amount_collected_on_time': self.total_collected_on_time,
                    'total_amount_collected_on_time_by_kpi': self.total_amount_collected_on_time_by_kpi,
                    'total_kpi_rate':self.total_kpi_rate,
                    'company_id':self.company_id.id
                })
        return True


    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_sync_kpi_lines(self):
        self._sync_kpi_lines()

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def _cron_generate_monthly_appraisals(self):
        """Auto-create a draft appraisal for every active salesperson
        (member of a Sales Team) for the current month, if one does not
        already exist."""
        today = fields.Date.today()
        month = '%02d' % today.month
        year = today.year

        salespeople = self.env['crm.team.member'].search([
            ('active', '=', True),
        ]).mapped('user_id')

        for user in salespeople:
            existing = self.search([
                ('', '=', user.id),
                ('month', '=', month),
                ('year', '=', year),
            ], limit=1)
            if not existing:
                employee = self.env['hr.employee'].search(
                    [('user_id', '=', user.id)], limit=1)
                self.create({
                    'salesperson_id': user.id,
                    'employee_id': employee.id if employee else False,
                    'month': month,
                    'year': year,
                })
        return True
