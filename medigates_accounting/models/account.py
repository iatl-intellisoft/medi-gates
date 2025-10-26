from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date, timedelta


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_cash_payment_method = fields.Boolean(
        string="Is Cash Payment Method",
        compute="_compute_is_cash_payment_method",
        store=False,
    )

    @api.depends('partner_id')
    def _compute_is_cash_payment_method(self):
        for rec in self:
	        rec.is_cash_payment_method = False  # <-- Default assignment
	        if rec.partner_id and rec.partner_id.property_inbound_payment_method_line_id:
	            method_line = rec.partner_id.property_inbound_payment_method_line_id
	            if method_line.journal_id and method_line.journal_id.type == 'cash':
	                rec.is_cash_payment_method = True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_paid = fields.Boolean(
        string="paid",
        store=False,
    )

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_validate(self):
        """Mark the corresponding installment lines as paid after payment is posted."""
        res = super().action_validate()

        for payment in self:
            # Find all related invoice move lines that are not paid
            for move in payment.move_id:
                # Match move lines by the payment date (or fully reconcile if needed)
                lines_to_pay = move.line_ids.filtered(
                    lambda l: l.balance == 0.0 and hasattr(l, 'is_paid') and not l.is_paid
                )
                lines_to_pay.write({'is_paid': True})

        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    private_custom = fields.Boolean(string="Private Customer")
    trust_custom = fields.Boolean(string="Trust Customer")



class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_date_act = fields.Date(
        string='Actual delivery  Date',
        copy=False,
        store=True,
        readonly=False,
    )



    def check_overdue_trusted_customers(self):
        today = date.today()
        overdue_invoices = self.search([
            ('partner_id.trust_custom', '=', True),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today),
        ])

        for invoice in overdue_invoices:
            message = f"🚨 Invoice {invoice.name} for trusted customer {invoice.partner_id.name} is overdue (Due: {invoice.invoice_date_due})."
            # Notify Salesperson
            if invoice.invoice_user_id:
                invoice.message_post(
                    body=message,
                    partner_ids=[invoice.invoice_user_id.partner_id.id],
                )
            # Notify Accountant Group (Optional)
            group = self.env.ref('account.group_account_invoice')
            for user in group.users:
                invoice.message_post(
                    body=message,
                    partner_ids=[user.partner_id.id],
                )
                

    @api.depends('invoice_payment_term_id', 'invoice_date', 'delivery_date_act', 'currency_id', 'amount_total_in_currency_signed', 'invoice_date_due')
    def _compute_needed_terms(self):
        AccountTax = self.env['account.tax']
        for invoice in self.with_context(bin_size=False):
            is_draft = invoice.id != invoice._origin.id
            invoice.needed_terms = {}
            invoice.needed_terms_dirty = True
            sign = 1 if invoice.is_inbound(include_receipts=True) else -1
            if invoice.is_invoice(True) and invoice.invoice_line_ids:
                if invoice.invoice_payment_term_id:
                    if is_draft:
                        tax_amount_currency = 0.0
                        tax_amount = tax_amount_currency
                        untaxed_amount_currency = 0.0
                        untaxed_amount = untaxed_amount_currency
                        sign = invoice.direction_sign
                        base_lines, _tax_lines = invoice._get_rounded_base_and_tax_lines(round_from_tax_lines=False)
                        AccountTax._add_accounting_data_in_base_lines_tax_details(base_lines, invoice.company_id, include_caba_tags=invoice.always_tax_exigible)
                        tax_results = AccountTax._prepare_tax_lines(base_lines, invoice.company_id)
                        for base_line, to_update in tax_results['base_lines_to_update']:
                            untaxed_amount_currency += sign * to_update['amount_currency']
                            untaxed_amount += sign * to_update['balance']
                        for tax_line_vals in tax_results['tax_lines_to_add']:
                            tax_amount_currency += sign * tax_line_vals['amount_currency']
                            tax_amount += sign * tax_line_vals['balance']
                    else:
                        tax_amount_currency = invoice.amount_tax * sign
                        tax_amount = invoice.amount_tax_signed
                        untaxed_amount_currency = invoice.amount_untaxed * sign
                        untaxed_amount = invoice.amount_untaxed_signed
                    invoice_payment_terms = invoice.invoice_payment_term_id._compute_terms(
                        date_ref=invoice.delivery_date_act or invoice.invoice_date or invoice.date or fields.Date.context_today(invoice),
                        currency=invoice.currency_id,
                        tax_amount_currency=tax_amount_currency,
                        tax_amount=tax_amount,
                        untaxed_amount_currency=untaxed_amount_currency,
                        untaxed_amount=untaxed_amount,
                        company=invoice.company_id,
                        cash_rounding=invoice.invoice_cash_rounding_id,
                        sign=sign
                    )
                    for term_line in invoice_payment_terms['line_ids']:
                        key = frozendict({
                            'move_id': invoice.id,
                            'date_maturity': fields.Date.to_date(term_line.get('date')),
                            'discount_date': invoice_payment_terms.get('discount_date'),
                        })
                        values = {
                            'balance': term_line['company_amount'],
                            'amount_currency': term_line['foreign_amount'],
                            'discount_date': invoice_payment_terms.get('discount_date'),
                            'discount_balance': invoice_payment_terms.get('discount_balance') or 0.0,
                            'discount_amount_currency': invoice_payment_terms.get('discount_amount_currency') or 0.0,
                        }
                        if key not in invoice.needed_terms:
                            invoice.needed_terms[key] = values
                        else:
                            invoice.needed_terms[key]['balance'] += values['balance']
                            invoice.needed_terms[key]['amount_currency'] += values['amount_currency']
                else:
                    invoice.needed_terms[frozendict({
                        'move_id': invoice.id,
                        'date_maturity': fields.Date.to_date(invoice.invoice_date_due),
                        'discount_date': False,
                        'discount_balance': 0.0,
                        'discount_amount_currency': 0.0
                    })] = {
                        'balance': invoice.amount_total_signed,
                        'amount_currency': invoice.amount_total_in_currency_signed,
                    }




