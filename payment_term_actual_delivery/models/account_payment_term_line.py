from odoo import fields, models


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    value = fields.Selection([

            ('delivery_date_act', 'Days After Actual Delivery Date')
    ]

    )