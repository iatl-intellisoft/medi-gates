from odoo import models, fields

class StockMoveIncoming(models.Model):
    _inherit = 'stock.move'

    purchase_ref = fields.Char(
        string='Purchase Ref',
        related='purchase_line_id.order_id.name',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='purchase_line_id.order_id.currency_id',
        store=True
    )
    stock_out_ref = fields.Char(
        string='Stock Out Ref',
        related='picking_id.origin',
        store=True
    )