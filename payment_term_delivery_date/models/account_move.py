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

    @api.onchange('delivery_date_act')
    def _onchange_delivery_date_act(self):
        self._recompute_payment_terms_lines()

