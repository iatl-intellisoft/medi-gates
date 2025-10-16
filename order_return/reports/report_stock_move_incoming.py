from odoo import models, fields

class ReportStockMoveIncoming(models.AbstractModel):
    _name = 'report.order_return.report_stock_move_incoming'
    _description = 'Incoming Stock Move Report'

    def _get_report_values(self, docids, data=None):
        domain = [('picking_type_code', '=', 'incoming')]
        stock_moves = self.env['stock.move'].search(domain)

        # Prepare data for the template
        docs = []
        for move in stock_moves:
            docs.append({
                'purchase_ref': move.purchase_line_id.order_id.name if move.purchase_line_id else '',
                'product_name': move.product_id.display_name,
                'qty': move.product_uom_qty,
                'price_unit': move.price_unit,
                'currency': move.purchase_line_id.order_id.currency_id.name if move.purchase_line_id else '',
                'stock_out_ref': move.picking_id.origin or '',
                'location_dest': move.location_dest_id.display_name,
                'state': move.state,
            })

        return {
            'doc_ids': docids,
            'doc_model': 'stock.move',
            'docs': docs,
            'company': self.env.company,
        }
