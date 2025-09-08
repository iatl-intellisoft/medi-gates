from odoo import models, fields, api

class InventoryMovementReportWizard(models.TransientModel):
    _name = 'inventory.movement.report.wizard'
    _description = 'Inventory Movement Report Wizard'

    product_id = fields.Many2one('product.product', string='Product')
    categ_id = fields.Many2one('product.category', string='Product Category')

    def action_print_report(self):
        domain = []
        if self.product_id:
            domain.append(('id', '=', self.product_id.id))
        elif self.categ_id:
            domain.append(('categ_id', '=', self.categ_id.id))

        products = self.env['product.product'].search(domain or [])

        return self.env.ref('your_module.action_report_inventory_movement_pdf').report_action(products)

        
from odoo import models, fields, api
from datetime import date

class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Salesperson Report Wizard'

    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    customer_city = fields.Char(string='Customer City')
    date_from = fields.Date(string='Date From', default=date.today)
    date_to = fields.Date(string='Date To', default=date.today)

    def action_print_report(self):
        domain = [('order_id.state', 'in', ['sale', 'done'])]

        if self.salesperson_id:
            domain.append(('order_id.user_id', '=', self.salesperson_id.id))
        if self.customer_city:
            domain.append(('order_id.partner_id.city', 'ilike', self.customer_city))
        if self.date_from:
            domain.append(('order_id.date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('order_id.date_order', '<=', self.date_to))

        lines = self.env['sale.order.line'].search(domain)

        return self.env.ref('medigates_sale.action_report_salesperson_pdf').report_action(
            lines, data={
                'form': {
                    'salesperson': self.salesperson_id.name if self.salesperson_id else '',
                    'city': self.customer_city or '',
                    'date_from': str(self.date_from),
                    'date_to': str(self.date_to),
                }
            }
        )
