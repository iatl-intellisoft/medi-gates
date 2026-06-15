# -*- coding: utf-8 -*-
from odoo import models, fields, _


class AccountPaymentTermLine(models.Model):
    """Extend Payment Term Lines with a new due-date computation option
    based on the Actual Delivery Date of the related invoice.
    """
    _inherit = 'account.payment.term.line'

    value = fields.Selection(
        selection_add=[
            ('delivery_date_act', '15 Days After Actual Delivery Date'),
        ],
        ondelete={'delivery_date_act': 'set default'},
    )
