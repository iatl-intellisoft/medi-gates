from datetime import timedelta

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _recompute_actual_delivery_due_date(self):
        for move in self:

            sale_order = self.env['sale.order'].search([
                ('name', '=', move.invoice_origin)
            ], limit=1)

            if not sale_order:
                continue

            if not sale_order.delivery_date_act:
                continue

            for line in move.invoice_payment_term_id.line_ids:

                if line.value != 'delivery_date_act':
                    continue

                due_date = (
                    sale_order.delivery_date_act
                    + timedelta(days=line.nb_days)
                )

                move.invoice_date_due = due_date