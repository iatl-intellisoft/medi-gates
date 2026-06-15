from odoo import fields, models

class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    delay_type = fields.Selection(
        selection_add=[
            ("actual_delivery", "Days After Actual Delivery Date")
        ]
    )
