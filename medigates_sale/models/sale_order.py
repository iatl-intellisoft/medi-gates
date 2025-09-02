from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    confirmed_delivery_date = fields.Date(string="Confirmed Delivery Date")
    customer_outside_local_city = fields.Boolean(string="Customer Outside Local City")


    def action_confirm(self):
        for order in self:
            insufficient_products = []

            for line in order.order_line:
                product = line.product_id

                if product.type != 'consu' and not product.is_storable:
                    continue  # Skip service and consumables

                ordered_qty = line.product_uom_qty
                available_qty = product.qty_available

                if ordered_qty > available_qty:
                    insufficient_products.append(
                        f"- {product.display_name}: Ordered {ordered_qty}, Available {available_qty}"
                    )

            if insufficient_products:
                message = _("Cannot confirm Sale Order '%s' due to insufficient stock:\n\n%s") % (
                    order.name,
                    "\n".join(insufficient_products)
                )
                raise ValidationError(message)

        # Call the original confirmation logic
        return super(SaleOrder, self).action_confirm()


    def _create_invoices(self, grouped=False, final=False):
        for order in self:
            if order.customer_outside_local_city and not order.confirmed_delivery_date:
                raise UserError(_(
                    "Invoice cannot be created because the Confirmed Delivery Date is missing "
                    "for a customer outside the local city."
                ))
        return super()._create_invoices(grouped=grouped, final=final)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

        private_custom = fields.Boolean(string="Private Customer")

    @api.onchange('order_id.partner_id.private_custom')
    def _onchange_partner_private_discount_lock(self):
        if self.order_id.partner_id.private_custom:
            self.private_custom = True

