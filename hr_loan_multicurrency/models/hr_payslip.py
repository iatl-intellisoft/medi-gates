# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


LOAN_INPUT_CODE = 'LOAN'


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    loan_line_id = fields.Many2one(
        'hr.loan.fx.line', string='قسط القرض المستقطع', readonly=True, copy=False,
        help='القسط الذي تم استقطاعه في هذه القسيمة، إن وجد.')

    def compute_sheet(self):
        """قبل الاحتساب: نحقن Other Input بكود LOAN بقيمة القسط المستحق
        محوّلة لعملة الشركة بسعر الصرف الفعلي بتاريخ نهاية الراتب (date_to).
        لا يتم لمس أي دالة أخرى من hr_payroll / hr_payroll_account."""
        for slip in self:
            slip._inject_loan_input()
        return super().compute_sheet()

    def _get_running_loan(self):
        self.ensure_one()
        return self.env['hr.loan.fx'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', 'in', ['approved', 'running']),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

    def _inject_loan_input(self):
        self.ensure_one()
        # نزيل أي سطر LOAN سابق (لو أعيد احتساب القسيمة أكثر من مرة قبل التثبيت)
        old_lines = self.input_line_ids.filtered(
            lambda l: l.code == LOAN_INPUT_CODE)
        if old_lines:
            old_lines.unlink()

        loan = self._get_running_loan()
        if not loan:
            return

        due_line = loan.get_due_installment(self.date_from, self.date_to)
        if not due_line:
            return

        company_currency = self.company_id.currency_id
        amount_company_currency = loan.currency_id._convert(
            due_line.amount_currency,
            company_currency,
            self.company_id,
            self.date_to or fields.Date.context_today(self),
        )

        input_type = self.env.ref(
            'hr_loan_multicurrency.hr_payslip_input_type_loan', raise_if_not_found=False)
        if not input_type:
            input_type = self.env['hr.payslip.input.type'].search(
                [('code', '=', LOAN_INPUT_CODE)], limit=1)

        self.env['hr.payslip.input'].create({
            'payslip_id': self.id,
            'input_type_id': input_type.id if input_type else False,
            'code': LOAN_INPUT_CODE,
            'name': _('استقطاع قسط قرض: %s') % loan.name,
            'amount': amount_company_currency,
        })
        self.loan_line_id = due_line.id

        

    def action_payslip_done(self):
        res = super().action_payslip_done()
        for slip in self:
            if slip.loan_line_id and not slip.loan_line_id.paid:
                loan = slip.loan_line_id.loan_id
                company_currency = slip.company_id.currency_id
                amount_company_currency = loan.currency_id._convert(
                    slip.loan_line_id.amount_currency,
                    company_currency,
                    slip.company_id,
                    slip.date_to or fields.Date.context_today(slip),
                )
                rate = (
                    amount_company_currency / slip.loan_line_id.amount_currency
                    if slip.loan_line_id.amount_currency else 0.0
                )
                slip.loan_line_id.mark_paid(slip, amount_company_currency, rate)
                # لو كانت هذه آخر دفعة، نقفل القرض
                if not loan.loan_line_ids.filtered(lambda l: not l.paid):
                    loan.state = 'done'
                elif loan.state == 'approved':
                    loan.state = 'running'
        return res
