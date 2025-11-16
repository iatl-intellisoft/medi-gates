from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sales_supervisor', 'Sales Supervisor Approval'), 
    ('accountant', 'Accountant Approval'),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]



class SaleOrder(models.Model):
    _inherit = 'sale.order'


    confirmed_delivery_date = fields.Date(string="Confirmed Delivery Date")
    customer_outside_local_city = fields.Boolean(string="Customer Outside Local City")
    global_discount = fields.Boolean(
        string='Global Discount',)
    # state = fields.Selection(
    #     selection_add=[('sales_supervisor', 'Sales Supervisor Approval'), ('accountant', 'Accountant Approval')])
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    
    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'accountant', 'sent'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False
        
    # def action_confirm(self):
    #     for order in self:
    #         insufficient_products = []

    #         for line in order.order_line:
    #             product = line.product_id

    #             if product.type != 'consu' and not product.is_storable:
    #                 continue  # Skip service and consumables

    #             ordered_qty = line.product_uom_qty
    #             available_qty = product.qty_available

    #             if ordered_qty > available_qty:
    #                 insufficient_products.append(
    #                     f"- {product.display_name}: Ordered {ordered_qty}, Available {available_qty}"
    #                 )

    #         if insufficient_products:
    #             message = _("Cannot confirm Sale Order '%s' due to insufficient stock:\n\n%s") % (
    #                 order.name,
    #                 "\n".join(insufficient_products)
    #             )
    #             raise ValidationError(message)

    #     # Call the original confirmation logic
    #     return super(SaleOrder, self).action_confirm()


    def _create_invoices(self, grouped=False, final=False):
        for order in self:
            if order.customer_outside_local_city and not order.confirmed_delivery_date:
                raise UserError(_(
                    "Invoice cannot be created because the Confirmed Delivery Date is missing "
                    "for a customer outside the local city."
                ))
        return super()._create_invoices(grouped=grouped, final=final)

    def action_sales_supervisor(self):
        self.write({'state': 'sales_supervisor'})

    def action_accountant(self):
        self.write({'state': 'accountant'})

    @api.model
    def create(self, vals):
        order = super().create(vals)
        if order.confirmed_delivery_date and order.invoice_ids:
            order.invoice_ids.write({'delivery_date_act': order.confirmed_delivery_date})
        return order

    def write(self, vals):
        res = super().write(vals)
        if 'confirmed_delivery_date' in vals:
            for order in self:
                if order.invoice_ids:
                    order.invoice_ids.write({'delivery_date_act': order.confirmed_delivery_date})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'product_uom_qty', 'product_uom')
    def _check_stock_qty_validation(self):
        """Prevent saving if ordered quantity exceeds available stock."""
        for line in self:
            # Skip display lines or missing product
            if not line.product_id or line.display_type:
                continue

            # Convert ordered quantity to product's base UoM (the one used in stock)
            qty_ordered_in_stock_uom = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id
            )

            qty_available = line.product_id.qty_available

            if qty_ordered_in_stock_uom > qty_available:
                raise ValidationError(
                    f"Not enough stock for {line.product_id.display_name}.\n"
                    f"Available: {qty_available} {line.product_id.uom_id.name}(s), "
                    f"Ordered: {qty_ordered_in_stock_uom:.2f} {line.product_id.uom_id.name}(s)."
                )


