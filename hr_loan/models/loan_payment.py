from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import html_translate


class HrLoanPayment(models.Model):
    """"""
    _name = 'loan.payment'
    _rec_name = 'reference'
    _inherit = ['mail.thread']
    _description = "Loan Payments as voucher"

    reference = fields.Char('Reference')
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True)
    loan_id = fields.Many2one('hr.loan', string="Loans",
                              domain="[('employee_id', '=', employee_id),('state','=','approve')]")
    loan_line_ids = fields.Many2many('hr.loan.line', string='Installments',
                                     domain="[('loan_id', '=', loan_id),('paid','=',False)]")
    amount = fields.Float('Amount', compute="_get_total_to_paid")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancel')
                              ], string="State", default='draft', track_visibility='onchange', copy=False, )
    voucher_id = fields.Many2one('account.move', string='Voucher', track_visibility='onchange')
    date = fields.Date(string="Date", default=date.today())

    def _get_total_to_paid(self):
        """
        A method to get total paid loan amount
        """
        total_to_paid_amount = 0.00
        for loan in self:
            for line in loan.loan_line_ids:
                total_to_paid_amount += line.paid_amount
            self.amount = total_to_paid_amount

    def action_confirmed(self):
        """
        A method to confirm loan payment
        """
        self.write({
            'state': 'confirmed'
        })

    def action_cancel(self):
        """
        A method to cancel loan payment
        """
        self.write({
            'state': 'cancel'
        })


    def action_approve(self):
        """
        A method to approve loan payment
        """
        if not self.loan_id.loan_type.emp_account_id or not self.loan_id.loan_type.treasury_account_id:
            raise UserError('UserError', "You must enter employee account & Treasury account and journal to approve ")
        if not self.loan_line_ids:
            raise UserError('UserError', 'You must compute Loan Request before Approved')
        for loan in self:
            journal_id = loan.loan_id.loan_type.journal_id.id
            emp_partner = loan.employee_id.work_contact_id
            if not emp_partner:
                raise ValidationError(_('Please add Partner for this Employee.'))
            line_ids = []
            loan_request_date = loan.date
            loan_currency = loan.loan_id.currency_id
            amount = loan.amount
            loan_name = 'Loan For ' + loan.employee_id.name
            reference = loan.reference
            journal_id = loan.loan_id.journal_id.id
            move_dict = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': loan_request_date,
            }
            # if loan_currency != company_currency and loan_currency.name == 'SDG':
            debit_line = (0, 0, {
                'name': loan_name,
                'partner_id': emp_partner.id,
                'account_id': loan.loan_id.loan_type.treasury_account_id.id,
                'journal_id': journal_id,
                'amount_currency': loan.amount,
                'currency_id': loan_currency.id,
                'date': loan_request_date,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'tax_line_id': 0.0,
            })
            line_ids.append(debit_line)
            credit_line = (0, 0, {
                'name': loan_name,
                'partner_id': emp_partner.id,
                'account_id': loan.loan_id.loan_type.emp_account_id.id,
                'journal_id': journal_id,
                'amount_currency': -loan.amount,
                'currency_id': loan_currency.id,
                'date': loan_request_date,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'tax_line_id': 0.0,
            })
            line_ids.append(credit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            self.write({'state': "approve", 'voucher_id': move.id})
            loan.loan_line_ids.write({'paid': True})
        return True

    @api.model
    def create(self, values):
        """
        Inherit create method to ensure loan lines was created and then create sequence
        """
        res = super(HrLoanPayment, self).create(values)
        if not res.loan_line_ids:
            raise ValidationError(_('Please add Lines Installments.'))
        loan = res.loan_id.name
        res.reference = loan + self.env['ir.sequence'].get('loan.payment') or ' '

        return res

    def unlink(self):
        """
        A method to delete loan payment
        """
        for payment in self:
            if payment.state not in ('draft',):
                raise UserError(_('You can not delete record not in draft state.'))
        return super(HrLoanPayment, self).unlink()
