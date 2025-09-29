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

    def get_loan(self):
        """
        A method to get posted and approved employee's loan
        """
        array = []
        domain = []
        for rec in self:
            rec.loan_ids.write({'payslip_id': False})
            loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', rec.employee_id.id),
                                                        ('paid', '=', False), ('paid_date', '>=', rec.date_from),
                                                        ('paid_date', '<=', rec.date_to),
                                                        
                                                        ])
            for loan in loan_ids:
                if loan.loan_id.state == 'approve':
                    array.append(loan.id)
            rec.loan_ids = array
        return array

    def compute_sheet(self):
        """
        inherit from compute_sheet to compute loan from payslip
        """
        for rec in self:
            rec.get_loan()
        return super(HrPayslip, rec.sudo()).compute_sheet()

    def action_payslip_done(self):
        """
        A method to loan from payslip
        """
        for rec in self:
            res = super(HrPayslip, rec.sudo()).action_payslip_done()
            loan_lines = rec.env['hr.loan.line'].search([('payslip_id', '=', rec.id)])
            if loan_lines:
                for line in loan_lines:
                    line.action_paid_amount()
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
