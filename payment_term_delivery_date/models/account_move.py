# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _recompute_delivery_date_due(self):
        for move in self:
            if not move.invoice_payment_term_id:
                continue

            if not move.delivery_date_act:
                continue

            term_line = move.invoice_payment_term_id.line_ids.filtered(
                lambda l: l.delay_type == 'delivery_date_act'
            )[:1]

            if not term_line:
                continue

            move.invoice_date_due = (
                move.delivery_date_act +
                timedelta(days=term_line.nb_days)
            )

    @api.onchange('invoice_payment_term_id', 'delivery_date_act')
    def _onchange_delivery_payment_term(self):
        self._recompute_delivery_date_due()

    def write(self, vals):
        res = super().write(vals)

        if (
            'delivery_date_act' in vals
            or 'invoice_payment_term_id' in vals
        ):
            self.filtered(
                lambda m: m.state == 'draft'
            )._recompute_delivery_date_due()

        return res
        
    def action_post(self):
        res = super().action_post()
    
        self._recompute_delivery_date_due()
    
        return res
