# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslip(models.Model):
    """"""
    _inherit = 'hr.payslip'

    def compute_total_paid_loan(self):
        """
        A method to compute total paid loan amount
        """
        total = 0.00
        for line in self.loan_ids:
            total += line.paid_amount
        self.total_amount_paid = total

    loan_ids = fields.One2many('hr.loan.line', 'payslip_id', string="Loans", readonly=True)
    total_amount_paid = fields.Float(string="Total Loan Amount", compute='compute_total_paid_loan')

    # def get_loan(self):
    #     """
    #     A method to get posted and approved employee's loan
    #     """
    #     array = []
    #     domain = []
    #     for rec in self:
    #         rec.loan_ids.write({'payslip_id': False})
    #         loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', rec.employee_id.id),
    #                                                     ('paid', '=', False), ('paid_date', '>=', rec.date_from),
    #                                                     ('paid_date', '<=', rec.date_to),
                                                        
    #                                                     ])
    #         for loan in loan_ids:
    #             if loan.loan_id.state == 'approve':
    #                 array.append(loan.id)
    #         rec.loan_ids = array
    #     return array

    def get_loan(self):
        """
        Method to fetch and assign loans to payslip where the loan is approved and 
        payment is scheduled within the payslip period.
        """
        HrLoanLine = self.env['hr.loan.line']

        for rec in self:
            # Clear previous loan line links
            if rec.loan_ids:
                rec.loan_ids.write({'payslip_id': False})

            # Find unpaid loan lines within the payslip date range
            loan_lines = HrLoanLine.search([
                ('employee_id', '=', rec.employee_id.id),
                ('paid', '=', False),
                ('paid_date', '>=', rec.date_from),
                ('paid_date', '<=', rec.date_to),
                ('loan_id.state', '=', 'approve')
            ])

            # Link loan lines to this payslip
            loan_lines.write({'payslip_id': rec.id})

            # Assign the loan lines to the record (only needed if loan_ids is computed/stored manually)
            rec.loan_ids = loan_lines

        return True
    def compute_sheet(self):
        self.get_loan()
    
        res = super().compute_sheet()
    
        for slip in self:
            for line in slip.line_ids:
                if line.salary_rule_id.currency_id:
                    line.currency_id = line.salary_rule_id.currency_id.id
    
        return res
        
    # def compute_sheet(self):
    #     self.get_loan()
    
    #     res = super().compute_sheet()
    
    #     for slip in self:
    #         loan = slip.loan_ids[:1]
    #         if not loan:
    #             continue
    
    #         loan_salary_line = slip.line_ids.filtered(lambda l: l.code == 'USDL')
    
    #         if loan_salary_line:
    #             loan_salary_line.write({
    #                 'currency_id': loan.loan_id.currency_id.id,
    #             })
    
    #     return res

    
    # def compute_sheet(self):
    #     """
    #     inherit from compute_sheet to compute loan from payslip
    #     """
    #     self.get_loan()
    #     return super(HrPayslip, self.sudo()).compute_sheet()
        
    # def action_payslip_done(self):
    #     """
    #     A method to loan from payslip
    #     """
    #     for rec in self:
    #         res = super(HrPayslip, rec.sudo()).action_payslip_done()
    #         loan_lines = rec.env['hr.loan.line'].search([('payslip_id', '=', rec.id)])
    #         if loan_lines:
    #             for line in loan_lines:
    #                 line.action_paid_amount()
    #     return res

    def action_payslip_done(self):
        """
        Mark loan installments as paid and update move line currencies.
        """
        for rec in self:
            res = super(HrPayslip, rec.sudo()).action_payslip_done()

            if rec.move_id:
                company_currency = rec.company_id.currency_id

                for move_line in rec.move_id.line_ids:
                    payslip_line = rec.line_ids.filtered(
                        lambda l: (
                            l.name == move_line.name
                            and abs(
                                l.total - (move_line.debit or move_line.credit)
                            ) < 0.00001
                        )
                    )[:1]

                    if (
                        payslip_line
                        and payslip_line.currency_id
                        and payslip_line.currency_id != company_currency
                    ):
                        amount = (
                            move_line.debit
                            if move_line.debit
                            else -move_line.credit
                        )

                        move_line.write({
                            'currency_id': payslip_line.currency_id.id,
                            'amount_currency': amount,
                        })

            loan_lines = self.env['hr.loan.line'].search([
                ('payslip_id', '=', rec.id)
            ])
            loan_lines.action_paid_amount()

        return res

    def action_payslip_cancel(self):
        """
        action_payslip_cancel method Inherited and update payslip and state to set loan in cancel state.
        """
        for rec in self:
            rec.loan_ids.write({'payslip_id': False, 'paid': False})
        return super(HrPayslip, self).action_payslip_cancel()

    def action_draft(self):
        """
        action_draft method Inherited and update payslip and state to set loan in cancel state.
        """
        for rec in self:
            rec.loan_ids.write({'payslip_id': False, 'paid': False})
        return super(HrPayslip, self).action_draft()








# from odoo import models
# from odoo.fields import Command
# from odoo.tools import float_is_zero


# class HrPayslip(models.Model):
#     _inherit = 'hr.payslip'

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        vals = super()._prepare_line_values(line, account_id, date, debit, credit)
        company_currency = self.company_id.currency_id
        currency = line.currency_id
        if currency and currency != company_currency:
            sign = 1 if debit else -1
            vals['currency_id'] = currency.id
            vals['amount_currency'] = sign * abs(line.foreign_amount)
        else:
            vals['currency_id'] = company_currency.id
            vals['amount_currency'] = 0.0
        return vals

    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = super()._get_existing_lines(line_ids, line, account_id, debit, credit)
        currency = line.currency_id or self.company_id.currency_id
        # منع دمج سطر أجنبي مع سطر آخر بعملة مختلفة حتى لو تطابق الاسم/الحساب
        return (
            line_id for line_id in existing_lines
            if line_id.get('currency_id') == currency.id
        )

    def _prepare_slip_lines(self, date, line_ids):
        """نفس منطق hr_payroll_account الأصلي، مع إصلاح تجميع amount_currency
        عند دمج سطرين (مثلاً لما batch_payroll_move_lines مفعّلة)."""
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        company_currency = self.company_id.currency_id
        new_lines = []

        for line in self.line_ids.filtered(lambda l: l.category_id):
            amount = line.total
            if line.code == 'NET':
                for tmp_line in self.line_ids.filtered(lambda l: l.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net:
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue

            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id

            if debit_account_id:
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0
                debit_line = next(self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit), False)
                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                    debit_line['tax_ids'] = [Command.link(tax_id) for tax_id in line.salary_rule_id.account_debit.tax_ids.ids]
                    new_lines.append(debit_line)
                else:
                    debit_line['debit'] += debit
                    debit_line['credit'] += credit
                    if debit_line.get('currency_id') and debit_line['currency_id'] != company_currency.id:
                        sign = 1 if debit else -1
                        debit_line['amount_currency'] += sign * abs(line.foreign_amount)

            if credit_account_id:
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = next(self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit), False)
                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                    credit_line['tax_ids'] = [Command.link(tax_id) for tax_id in line.salary_rule_id.account_credit.tax_ids.ids]
                    new_lines.append(credit_line)
                else:
                    credit_line['debit'] += debit
                    credit_line['credit'] += credit
                    if credit_line.get('currency_id') and credit_line['currency_id'] != company_currency.id:
                        sign = 1 if debit else -1
                        credit_line['amount_currency'] += sign * abs(line.foreign_amount)

        return new_lines
        
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
