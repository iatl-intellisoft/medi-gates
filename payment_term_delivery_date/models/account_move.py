# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, models
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_payment_terms_computation_date(self):
        self.ensure_one()
        if self.delivery_date_act:
            return self.delivery_date_act
        return super()._get_payment_terms_computation_date()

    def _recompute_payment_terms_lines(self):
        for move in self:
            super(AccountMove, move.with_context(
                delivery_date_act=move.delivery_date_act
            ))._recompute_payment_terms_lines()
        return True

    @api.onchange('delivery_date_act')
    def _onchange_delivery_date_act(self):
        if self.invoice_payment_term_id:
            self._recompute_payment_terms_lines()

    def _get_payment_terms_computation_date(self):
        self.ensure_one()

        if self.delivery_date_act:
            return self.delivery_date_act

        return super()._get_payment_terms_computation_date()

    def _recompute_payment_terms_lines(self):
        for move in self:
            super(
                AccountMove,
                move.with_context(
                    delivery_date_act=move.delivery_date_act
                )
            )._recompute_payment_terms_lines()

        return True

    @api.onchange('delivery_date_act')
    def _onchange_delivery_date_act(self):
        for move in self:
            if move.invoice_payment_term_id:
                move._recompute_payment_terms_lines()

    def write(self, vals):
        delivery_date_changed = 'delivery_date_act' in vals

        result = super().write(vals)

        if delivery_date_changed:
            for move in self:
                if (
                    move.state == 'posted'
                    and move.delivery_date_act
                    and move.invoice_payment_term_id
                ):
                    move._recompute_payment_terms_lines()

        return result
