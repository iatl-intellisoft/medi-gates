from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        res = super().write(vals)

        if 'delivery_date_act' in vals:

            for order in self:

                invoices = order.invoice_ids.filtered(
                    lambda x: x.state == 'draft'
                )

                invoices._recompute_actual_delivery_due_date()

        return res