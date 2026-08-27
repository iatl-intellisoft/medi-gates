# -*- coding: utf-8 -*-
import base64
import io
from datetime import datetime

from odoo import fields, models
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class ProductionReceiptReportWizard(models.TransientModel):
    _name = 'production.receipt.report.wizard'
    _description = 'تقرير كميات وتكلفة المنتجات النازلة للمخزن من الإنتاج'

    date_from = fields.Date(string='من تاريخ', required=True)
    date_to = fields.Date(string='إلى تاريخ', required=True,
                           default=fields.Date.context_today)
    product_id = fields.Many2one('product.product', string='منتج محدد (اختياري)')
    file_data = fields.Binary(string='ملف التقرير', readonly=True)
    file_name = fields.Char(string='اسم الملف', readonly=True)

    def _get_domain(self):
        domain = [
            ('production_id', '!=', False),
            ('state', '=', 'done'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        return domain

    def action_generate_xlsx(self):
        self.ensure_one()
        if xlsxwriter is None:
            raise UserError('مكتبة xlsxwriter غير متاحة على السيرفر.')

        moves = self.env['stock.move'].search(
            self._get_domain(), order='date asc'
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('تقرير الإنتاج')
        sheet.right_to_left()

        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_fmt = workbook.add_format({'border': 1, 'align': 'center'})
        money_fmt = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0.00'})
        date_fmt = workbook.add_format({'border': 1, 'align': 'center', 'num_format': 'yyyy-mm-dd'})

        headers = ['أمر الإنتاج', 'المنتج', 'الكود', 'تاريخ النزول للمخزن',
                   'الكمية', 'الوحدة', 'إجمالي الكوست', 'كوست الوحدة']
        widths = [18, 30, 15, 18, 12, 10, 16, 14]
        for col, (h, w) in enumerate(zip(headers, widths)):
            sheet.write(0, col, h, header_fmt)
            sheet.set_column(col, col, w)

        row = 1
        total_qty = 0.0
        total_value = 0.0
        for move in moves:
            production = move.production_id
            qty = move.product_uom_qty or move.quantity or 0.0
            unit_cost = move.product_id.standard_price or 0.0
            value = qty * unit_cost

            sheet.write(row, 0, production.name or '', cell_fmt)
            sheet.write(row, 1, move.product_id.display_name or '', cell_fmt)
            sheet.write(row, 2, move.product_id.default_code or '', cell_fmt)
            move_dt = fields.Datetime.from_string(move.date) if move.date else None
            if move_dt:
                sheet.write_datetime(row, 3, move_dt, date_fmt)
            else:
                sheet.write(row, 3, '', cell_fmt)
            sheet.write(row, 4, qty, cell_fmt)
            sheet.write(row, 5, move.product_uom.name or '', cell_fmt)
            sheet.write(row, 6, value, money_fmt)
            sheet.write(row, 7, unit_cost, money_fmt)

            total_qty += qty
            total_value += value
            row += 1

        total_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9E1F2'
        })
        total_money_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9E1F2',
            'num_format': '#,##0.00'
        })
        sheet.write(row, 0, 'الإجمالي', total_fmt)
        sheet.merge_range(row, 1, row, 3, '', total_fmt)
        sheet.write(row, 4, total_qty, total_fmt)
        sheet.write(row, 5, '', total_fmt)
        sheet.write(row, 6, total_value, total_money_fmt)
        sheet.write(row, 7, '', total_fmt)

        workbook.close()
        output.seek(0)

        file_name = 'production_receipt_report_%s.xlsx' % datetime.now().strftime('%Y%m%d_%H%M%S')
        self.write({
            'file_data': base64.b64encode(output.read()),
            'file_name': file_name,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=file_data&filename_field=file_name&download=true' % (
                self._name, self.id),
            'target': 'self',
        }
