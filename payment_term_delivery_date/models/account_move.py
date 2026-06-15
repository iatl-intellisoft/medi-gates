# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _apply_delivery_date_due_date(self):
        for move in self:
            if not move.invoice_payment_term_id:
                continue

            if not move.delivery_date_act:
                continue

            delivery_line = move.invoice_payment_term_id.line_ids.filtered(
                lambda l: l.delay_type == 'delivery_date_act'
            )[:1]

            if not delivery_line:
                continue

            move.invoice_date_due = (
                move.delivery_date_act
                + timedelta(days=delivery_line.nb_days)
            )

    @api.onchange(
        'delivery_date_act',
        'invoice_payment_term_id'
    )
    def _onchange_delivery_date_due(self):
        self._apply_delivery_date_due_date()

    def write(self, vals):
        res = super().write(vals)

        if (
            'delivery_date_act' in vals
            or 'invoice_payment_term_id' in vals
        ):
            self.filtered(
                lambda m: m.state == 'draft'
            )._apply_delivery_date_due_date()

        return res
