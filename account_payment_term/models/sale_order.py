from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        res = super().write(vals)

        if "actual_delivery_date" in vals:

            for order in self:

                invoices = self.env["account.move"].search([
                    ("invoice_origin", "=", order.name),
                    ("state", "=", "draft"),
                    ("move_type", "=", "out_invoice"),
                ])

                for invoice in invoices:
                    invoice._onchange_invoice_payment_term_id()

        return res