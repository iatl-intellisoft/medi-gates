# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    delay_type = fields.Selection(
        selection_add=[
            ('delivery_date_act', 'Days After Actual Delivery Date'),
        ],
        ondelete={'delivery_date_act': 'set default'},
    )
