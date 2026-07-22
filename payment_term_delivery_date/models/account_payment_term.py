# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    delay_type = fields.Selection(
        selection_add=[
            ('delivery_date_act', 'Days After Actual Delivery Date'),
        ],
        ondelete={'delivery_date_act': 'set default'},
    )

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    def _compute_terms(
        self,
        date_ref,
        currency,
        company,
        tax_amount,
        tax_amount_currency,
        sign,
        untaxed_amount,
        untaxed_amount_currency,
        cash_rounding=None,
        delivery_date_act=False,
    ):
        result = super()._compute_terms(
            date_ref,
            currency,
            company,
            tax_amount,
            tax_amount_currency,
            sign,
            untaxed_amount,
            untaxed_amount_currency,
            cash_rounding=cash_rounding,
        )

        if not delivery_date_act:
            return result

        for line, value in zip(self.line_ids, result):
            if line.delay_type == 'delivery_date_act':
                value['date'] = (
                    delivery_date_act +
                    timedelta(days=line.nb_days)
                )

        return result
