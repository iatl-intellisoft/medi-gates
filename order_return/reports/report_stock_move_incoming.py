from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_ref = fields.Char(string='Purchase Ref', compute='_compute_purchase_ref', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_purchase_ref', store=True)
    stock_out_ref = fields.Char(string='Stock Out Ref', related='picking_id.origin', store=True)

    @api.depends('picking_id')
    def _compute_purchase_ref(self):
        for move in self:
            purchase = self.env['purchase.order'].search([('name', '=', move.picking_id.origin)], limit=1)
            if purchase:
                move.purchase_ref = purchase.name
                move.currency_id = purchase.currency_id
            else:
                move.purchase_ref = move.picking_id.origin or ''
                move.currency_id = False