from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE 
from odoo import models, fields, tools, api
class SaleReportPosted2(models.Model):
    _name = "sale.report.posted"
    _description = "Sales Analysis Report By Posted Invoice"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'


    date = fields.Date(string="Invoice Date")

    order_reference = fields.Char(string="Sales Order")

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )

    user_id = fields.Many2one(
        'res.users',
        string="Salesperson"
    )

    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team"
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company"
    )

    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )

    product_uom_qty = fields.Float(
        string="Quantity"
    )

    price_unit = fields.Float(
        string="Unit Price"
    )

    price_subtotal = fields.Float(
        string="Untaxed Amount"
    )

    price_total = fields.Float(
        string="Total"
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice"
    )

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string="Status")

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency"
    )

    def action_open_order(self):
        self.ensure_one()

        sale_order = self.env['sale.order'].search([
            ('name', '=', self.order_reference)
        ], limit=1)

        if not sale_order:
            return False

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_report_posted AS (

                SELECT

                    ROW_NUMBER() OVER() AS id,

                    am.invoice_date AS date,

                    so.name AS order_reference,

                    so.partner_id AS partner_id,

                    so.user_id AS user_id,

                    so.team_id AS team_id,

                    am.company_id AS company_id,

                    aml.product_id AS product_id,

                    aml.quantity AS product_uom_qty,

                    aml.price_unit AS price_unit,

                    aml.price_subtotal AS price_subtotal,

                    aml.price_total AS price_total,

                    am.id AS invoice_id,

                    so.state AS state,

                    am.currency_id AS currency_id

                FROM account_move_line aml

                INNER JOIN account_move am
                    ON am.id = aml.move_id

                INNER JOIN sale_order_line_invoice_rel sol_rel
                    ON sol_rel.invoice_line_id = aml.id

                INNER JOIN sale_order_line sol
                    ON sol.id = sol_rel.order_line_id

                INNER JOIN sale_order so
                    ON so.id = sol.order_id

                WHERE
                    am.state = 'posted'
                    AND am.move_type = 'out_invoice'
                    AND so.invoice_status = 'invoiced'
                    AND so.state != 'cancel'
                    AND aml.display_type IS NULL

            )
        """)
