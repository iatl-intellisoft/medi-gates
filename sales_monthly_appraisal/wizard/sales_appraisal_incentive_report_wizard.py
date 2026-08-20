# -*- coding: utf-8 -*-
import io
import base64
import xlsxwriter
from odoo import api, fields, models
from odoo.exceptions import UserError

MONTH_SELECTION = [
    ('01', 'January'), ('02', 'February'), ('03', 'March'),
    ('04', 'April'), ('05', 'May'), ('06', 'June'),
    ('07', 'July'), ('08', 'August'), ('09', 'September'),
    ('10', 'October'), ('11', 'November'), ('12', 'December'),
]


class SalesAppraisalIncentiveReportWizard(models.TransientModel):
    _name = 'sales.appraisal.incentive.report.wizard'
    _description = 'Sales Appraisal Incentive Excel Report Wizard'

    month = fields.Selection(
        MONTH_SELECTION, string='Month', required=True,
        default=lambda self: fields.Date.today().strftime('%m'),
    )
    year = fields.Integer(
        string='Year', required=True,
        default=lambda self: fields.Date.today().year,
    )
    excel_file = fields.Binary(string='Excel File', readonly=True)
    excel_filename = fields.Char(string='Filename', readonly=True)

    def _get_records(self):
        domain = [
            ('month', '=', self.month),
            ('year', '=', self.year),
        ]
        # كل المناديب اللي عندهم سجل في الشهر/السنة دي
        return self.env['sales.appraisal.incentive'].search(
            domain, order='salesperson_id')

    def action_print_excel(self):
        self.ensure_one()
        records = self._get_records()
        if not records:
            raise UserError('لا توجد بيانات لأي مندوب في هذا الشهر/السنة.')

        month_labels = dict(MONTH_SELECTION)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Incentives')

        title_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
        })
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1,
            'align': 'center', 'valign': 'vcenter',
        })
        cell_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'border': 1, 'num_format': '0.00%'})

        headers = [
            'Salesperson', 'Total Amount Collected', 'Total Amount Collected (KPI)',
            'Total Collected On Time', 'Total Collected On Time (KPI)',
            'Total KPI Rate (%)', 'Company',
        ]

        # عنوان التقرير
        sheet.merge_range(0, 0, 0, len(headers) - 1,
                           'Sales Incentive Report - %s %s' % (month_labels.get(self.month), self.year),
                           title_format)

        for col, title in enumerate(headers):
            sheet.write(1, col, title, header_format)

        row = 2
        total_collected = total_collected_kpi = total_on_time = total_on_time_kpi = 0.0
        for rec in records:
            sheet.write(row, 0, rec.salesperson_id.name or '', cell_format)
            sheet.write(row, 1, rec.total_amount_collected, money_format)
            sheet.write(row, 2, rec.total_amount_collected_by_kpi, money_format)
            sheet.write(row, 3, rec.total_amount_collected_on_time, money_format)
            sheet.write(row, 4, rec.total_amount_collected_on_time_by_kpi, money_format)
            sheet.write(row, 5, rec.total_kpi_rate, percent_format)
            sheet.write(row, 6, rec.company_id.name or '', cell_format)

            total_collected += rec.total_amount_collected
            total_collected_kpi += rec.total_amount_collected_by_kpi
            total_on_time += rec.total_amount_collected_on_time
            total_on_time_kpi += rec.total_amount_collected_on_time_by_kpi
            row += 1

        # صف الإجمالي
        total_format = workbook.add_format({
            'bold': True, 'border': 1, 'bg_color': '#F2F2F2', 'num_format': '#,##0.00',
        })
        sheet.write(row, 0, 'Total', workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#F2F2F2'}))
        sheet.write(row, 1, total_collected, total_format)
        sheet.write(row, 2, total_collected_kpi, total_format)
        sheet.write(row, 3, total_on_time, total_format)
        sheet.write(row, 4, total_on_time_kpi, total_format)
        sheet.write(row, 5, '', workbook.add_format({'border': 1, 'bg_color': '#F2F2F2'}))
        sheet.write(row, 6, '', workbook.add_format({'border': 1, 'bg_color': '#F2F2F2'}))

        for col, width in enumerate([25, 20, 22, 20, 22, 15, 20]):
            sheet.set_column(col, col, width)

        workbook.close()
        output.seek(0)

        self.excel_file = base64.b64encode(output.read())
        self.excel_filename = 'Sales_Incentives_%s_%s.xlsx' % (self.month, self.year)

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=excel_file&filename_field=excel_filename&download=true' % (
                self._name, self.id),
            'target': 'self',
        }