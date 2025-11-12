# -*- coding: utf-8 -*-

from odoo import fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_return_id = fields.Many2one('order.return', string='Return Order', ondelete='set null')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.move_ids_without_package:
            if self.stock_return_id:
                self.stock_return_id.write({'state': 'done'})
        return res
