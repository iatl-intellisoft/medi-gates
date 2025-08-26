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



class ResPartner(models.Model):
    _inherit = 'res.partner'

    private_custom = fields.Boolean(string="Private Customer")
    trust_custom = fields.Boolean(string="Trust Customer")



class AccountMove(models.Model):
    _inherit = 'account.move'

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

    # @api.model
    # def _notify_due_soon_invoices(self):
    #     target_date = fields.Date.today() + timedelta(days=2)

    #     # Find upcoming due invoices
    #     upcoming_invoices = self.search([
    #         ('move_type', '=', 'out_invoice'),
    #         ('state', '=', 'posted'),
    #         ('payment_state', '=', 'not_paid'),
    #         ('invoice_date_due', '=', target_date),
    #     ])

    #     for invoice in upcoming_invoices:
    #         message = f"Invoice <b>{invoice.name}</b> is due in 2 days."

    #         # Post message in chatter
    #         invoice.message_post(
    #             body=message,
    #             subtype_xmlid="mail.mt_note",
    #         )

    #         # Create activity for salesperson (invoice_user_id)
    #         if invoice.invoice_user_id:
    #             self.env['mail.activity'].create({
    #                 'res_model_id': self.env['ir.model']._get('account.move').id,
    #                 'res_id': invoice.id,
    #                 'user_id': invoice.invoice_user_id.id,
    #                 'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #                 'summary': 'raja Upcoming Due Invoice',
    #                 'note': message,
    #                 'date_deadline': target_date,
    #             })

    #         # Also notify internal user assigned to the customer
    #         for user in invoice.partner_id.user_ids:
    #             self.env['mail.activity'].create({
    #                 'res_model_id': self.env['ir.model']._get('account.move').id,
    #                 'res_id': invoice.id,
    #                 'user_id': user.id,
    #                 'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #                 'summary': 'Customer Invoice Due Soon',
    #                 'note': message,
    #                 'date_deadline': target_date,
    #             })



class ResUsers(models.Model):
    _inherit = 'res.users'

    todo_trusted_overdue_count = fields.Integer(
        string="Trusted Overdue Invoices",
        compute='_compute_todo_trusted_overdue_count'
    )

    def _compute_todo_trusted_overdue_count(self):
        today = date.today()
        AccountMove = self.env['account.move'].sudo()

        for user in self:
            # Get invoices where user is responsible (invoice_user_id)
            overdue = AccountMove.search([
                ('partner_id.trust_custom', '=', True),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
                ('invoice_date_due', '<', today),
                ('invoice_user_id', '=', user.id),
            ])
            user.todo_trusted_overdue_count = len(overdue)
