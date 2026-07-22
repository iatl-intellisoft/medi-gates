# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OrderReturnLine(models.TransientModel):
    _inherit = 'order.return.picking.line'

    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Line', index=True)


class OrderReturnPicking(models.TransientModel):
    _inherit = 'order.return.picking'

    @api.model
    def default_get(self, fields):
        rec = super(OrderReturnPicking, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'purchase.order':
            active_id = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            rec.update({'is_purchase': True,
                        'purchase_id': active_id.id})
        return rec

    purchase_picking_id = fields.Many2one("stock.picking", string="Picking", required=False, )
    is_purchase = fields.Boolean(string="Is Purchase", )
    purchase_id = fields.Many2one("purchase.order", string="Purchase", required=False, )

    @api.onchange('purchase_picking_id')
    def _onchange_purchase_picking_id(self):
        self.picking_id = self.purchase_picking_id.id

    def _prepare_order_return_vals(self):
        values = super(OrderReturnPicking, self)._prepare_order_return_vals()
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'purchase.order':
            active_id = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            values.update({'purchase_id': active_id.id,
                           'purchase_picking_id': self.purchase_picking_id.id,
                           'partner_id': active_id.partner_id.id,
                           'origin': active_id.name,
                           'return_type': 'purchase',
                           })
        return values

    def create_order_returns(self):
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'purchase.order':
            values = self._prepare_order_return_vals()
            order_return = self.env['order.return'].create(values)
            for line in self.product_return_moves:
                self.env['order.return.line'].create({
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'qty_return': line.quantity,
                    'return_id': order_return.id,
                    'move_id': line.move_id.id,
                    'to_refund': line.to_refund,
                    'price_unit': line.purchase_line_id.price_unit,
                    'discount': line.purchase_line_id.discount,
                    'purchase_order_id': line.purchase_line_id.id,
                    'analytic_distribution': line.purchase_line_id.analytic_distribution,
                    'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
                })
        else:
            return super(OrderReturnPicking, self).create_order_returns()

    @api.model
    def _prepare_order_return_picking_line_vals_from_move(self, stock_move):
        rec = super(OrderReturnPicking, self)._prepare_order_return_picking_line_vals_from_move(stock_move=stock_move)

        rec.update({'purchase_line_id': stock_move.purchase_line_id.id})

        return rec
