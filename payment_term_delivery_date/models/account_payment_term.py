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

    # -*- coding: utf-8 -*-
from odoo import models
from datetime import timedelta


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    def _compute_terms(self, date_ref, currency, company, tax_amount,
                        tax_amount_currency, sign, untaxed_amount,
                        untaxed_amount_currency, cash_rounding=None,
                        delivery_date_act=False):
        result = super()._compute_terms(
            date_ref, currency, company, tax_amount, tax_amount_currency,
            sign, untaxed_amount, untaxed_amount_currency,
            cash_rounding=cash_rounding,
        )
        base_date = delivery_date_act or self.env.context.get('delivery_date_act') or date_ref
        if not base_date:
            return result

        for line, value in zip(self.line_ids, result.get('line_ids', [])):
            if line.delay_type == 'delivery_date_act':
                value['date'] = base_date + timedelta(days=line.nb_days)

        return result

    # def _compute_terms(self, date_ref, currency, company, tax_amount,
    #                     tax_amount_currency, sign, untaxed_amount,
    #                     untaxed_amount_currency, cash_rounding=None,
    #                     delivery_date_act=False):
    #     result = super()._compute_terms(
    #         date_ref, currency, company, tax_amount, tax_amount_currency,
    #         sign, untaxed_amount, untaxed_amount_currency,
    #         cash_rounding=cash_rounding,
    #     )
    #     delivery_date_act = delivery_date_act or self.env.context.get('delivery_date_act')
    #     if not delivery_date_act:
    #         return result
    #     for line, value in zip(self.line_ids, result):
    #         if line.delay_type == 'delivery_date_act':
    #             value['date'] = delivery_date_act + timedelta(days=line.nb_days)
    #     return result
                            
    # def _compute_terms(
    #     self,
    #     date_ref,
    #     currency,
    #     company,
    #     tax_amount,
    #     tax_amount_currency,
    #     sign,
    #     untaxed_amount,
    #     untaxed_amount_currency,
    #     cash_rounding=None,
    #     delivery_date_act=False,
    # ):
    #     result = super()._compute_terms(
    #         date_ref,
    #         currency,
    #         company,
    #         tax_amount,
    #         tax_amount_currency,
    #         sign,
    #         untaxed_amount,
    #         untaxed_amount_currency,
    #         cash_rounding=cash_rounding,
    #     )

    #     if not delivery_date_act:
    #         return result

    #     for line, value in zip(self.line_ids, result):
    #         if line.delay_type == 'delivery_date_act':
    #             value['date'] = (
    #                 delivery_date_act +
    #                 timedelta(days=line.nb_days)
    #             )

    #     return result
