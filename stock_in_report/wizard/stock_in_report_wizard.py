# -*- coding: utf-8 -*-
import io
import base64
from datetime import datetime, time

from odoo import models, fields, api
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class StockInReportWizard(models.TransientModel):
    _name = 'stock.in.report.wizard'
    _description = 'تقرير المنتجات الداخلة للمخزن خلال فترة'

    date_from = fields.Date(string='من تاريخ', required=True)
    date_to = fields.Date(string='الى تاريخ', required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='المخزن (اختياري)',
        help='اتركه فارغ لعرض كل المخازن')

    state = fields.Selection(
        [('choose', 'اختيار الفترة'), ('done', 'تم التجهيز')],
        default='choose')
    xlsx_file = fields.Binary(string='ملف الإكسيل')
    file_name = fields.Char(string='اسم الملف')

    def action_generate_xlsx(self):
        self.ensure_one()
        if not xlsxwriter:
            raise UserError('مكتبة xlsxwriter غير متاحة على السيرفر.')
        if self.date_from > self.date_to:
            raise UserError('تاريخ البداية لازم يكون قبل تاريخ النهاية.')

        date_from_dt = datetime.combine(self.date_from, time.min)
        date_to_dt = datetime.combine(self.date_to, time.max)

        domain = [
            ('create_date', '>=', date_from_dt),
            ('create_date', '<=', date_to_dt),
            ('quantity', '>', 0),  # الكميات الداخلة فقط (وارد)
        ]
        if self.warehouse_id:
            domain.append(
                ('stock_move_id.location_dest_id.warehouse_id', '=', self.warehouse_id.id))

        layers = self.env['stock.valuation.layer'].search(domain)
        if not layers:
            raise UserError('لا توجد حركات وارد للمنتجات في الفترة المحددة.')

        # تجميع البيانات لكل منتج
        data = {}
        for layer in layers:
            product = layer.product_id
            if product.id not in data:
                data[product.id] = {
                    'product': product,
                    'qty': 0.0,
                    'value': 0.0,
                }
            data[product.id]['qty'] += layer.quantity
            data[product.id]['value'] += layer.value

        # بناء ملف الإكسيل
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('تقرير الوارد')
        sheet.right_to_left()

        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_fmt = workbook.add_format({'border': 1, 'align': 'center'})
        num_fmt = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0.00'})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})

        sheet.merge_range(
            0, 0, 0, 5,
            f'تقرير المنتجات الداخلة للمخزن من {self.date_from} الى {self.date_to}',
            title_fmt)

        headers = ['كود المنتج', 'اسم المنتج', 'وحدة القياس', 'الكمية الداخلة',
                   'متوسط تكلفة الوحدة', 'اجمالي الكوست']
        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_fmt)

        row = 3
        total_qty = 0.0
        total_value = 0.0
        for vals in data.values():
            product = vals['product']
            qty = vals['qty']
            value = vals['value']
            avg_cost = value / qty if qty else 0.0

            sheet.write(row, 0, product.default_code or '', cell_fmt)
            sheet.write(row, 1, product.name or '', cell_fmt)
            sheet.write(row, 2, product.uom_id.name or '', cell_fmt)
            sheet.write(row, 3, qty, num_fmt)
            sheet.write(row, 4, avg_cost, num_fmt)
            sheet.write(row, 5, value, num_fmt)

            total_qty += qty
            total_value += value
            row += 1

        total_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9E1F2',
            'num_format': '#,##0.00'
        })
        sheet.write(row, 2, 'الاجمالي', total_fmt)
        sheet.write(row, 3, total_qty, total_fmt)
        sheet.write(row, 4, '', total_fmt)
        sheet.write(row, 5, total_value, total_fmt)

        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 35)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 5, 18)

        workbook.close()
        output.seek(0)

        self.write({
            'xlsx_file': base64.b64encode(output.read()),
            'file_name': f'stock_in_report_{self.date_from}_{self.date_to}.xlsx',
            'state': 'done',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.in.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
