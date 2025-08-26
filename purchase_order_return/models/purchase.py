# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_done = fields.Boolean('Delivery done', compute='_check_delivery_state', default=False)
    purchase_count = fields.Integer(string='Picking', compute='_compute_purchase_count')

    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = rec.env['order.return'].search_count([('purchase_id', '=', rec.id)])

    def action_open_order_return(self):
        return {
            'name': 'Return',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'order.return',
            'context': {'search_default_purchase_id' : self.id, 'default_return_type': 'purchase'},
            'domain': [('purchase_id', '=', self.id)],
            'target': 'current',

        }

    def _check_delivery_state(self):
        self.delivery_done = False
        if self.picking_ids:
            for rec in self.picking_ids:
                if rec[0].state == 'done':
                    self.delivery_done = True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_return = fields.Float("Return Qty", digits='Product Unit of Measure', required=False, readonly=True)
