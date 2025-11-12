# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import api, fields, models, _
import xlsxwriter
import base64
from io import BytesIO


class HrPayrollBatch(models.Model):
    _inherit = 'hr.payslip.run'

    usd_rate = fields.Float(string="Usd Rate")

    # def print_excel(self):
    #     file_name = _('Payslip Reports.xlsx')
    #     fp = BytesIO()
    #     workbook = xlsxwriter.Workbook(fp)
    #     excel_sheet = workbook.add_worksheet('الاجر الشهري')
    #     excel_sheet.right_to_left()
    #     header_format = workbook.add_format(
    #         {'align': 'center', 'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 4})
    #     date_style = workbook.add_format({'text_wrap': True, 'border': 1, 'num_format': 'dd-mm-yyyy'})
    #     base_format = workbook.add_format(
    #         {'font_color': 'black', 'border': 4})
    #     excel_sheet.set_column('B:B', 20, )
    #     excel_sheet.set_column('A:A', 5, )
    #     excel_sheet.set_column('C:T', 11, )

    #     excel_sheet.merge_range('R2:S2', 'حالة الأجر', header_format)

    #     row = 2
    #     col = 0

    #     excel_sheet.write(row, col, 'رقم', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'الإسم', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'القسم', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'المرتب', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'الحافز', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'الإجمالي', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'ضمان إجتماعي', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'سلفية طويلة', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, ' نصف راتب وكشوفات', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'غياب', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'تاخير', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'إستقطاعات أخرى ', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'إستقطاع فطور ', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'إجمالي الإسقطاعات ', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'الصافي ', header_format)
    #     col += 1
    #     excel_sheet.write(row, col, 'التوقيع ', header_format)
    #     col += 1
    #     # excel_sheet.write(row, col, 'موقوف ', header_format)
    #     # col += 1

    #     col = 0
    #     row += 1
    #     counter = 1
    #     total_payslip = 0
    #     total_bouns_wage =0 
    #     total = 0
    #     total_si = 0
    #     total_ls = 0
    #     total_lc = 0
    #     total_lz = 0
    #     total_abs = 0
    #     total_late = 0
    #     total_breakfast = 0
    #     total_tot =  0
    #     total_net = 0
    #     for payslip in self.slip_ids:
    #         employee = payslip.employee_id

    #         total_payslip += payslip.contract_id.wage
    #         total_bouns_wage += payslip.contract_id.bouns_wage
    #         total =  total_payslip + total_bouns_wage


    #         excel_sheet.write(row, col, counter, base_format)
    #         col += 1
    #         excel_sheet.write(row, col, employee.name, base_format)
    #         col += 1
    #         excel_sheet.write(row, col, employee.department_id.name, base_format)
    #         col += 1
    #         excel_sheet.write(row, col, payslip.contract_id.wage, base_format)
    #         col += 1
    #         excel_sheet.write(row, col, payslip.contract_id.bouns_wage, base_format)
    #         col += 1
    #         excel_sheet.write(row, col, payslip.contract_id.wage + payslip.contract_id.bouns_wage, base_format)
    #         col += 1
    #         SI_id = payslip.line_ids.search([('code', '=', 'SI'), ('slip_id', '=', payslip.id)]).ids
    #         SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
    #         total_si += SI
    #         excel_sheet.write(row, col, SI, base_format)
    #         col += 1
    #         LON_A_id = payslip.line_ids.search([('code', '=', 'LOANC'), ('slip_id', '=', payslip.id)]).ids
    #         LS = self.env['hr.payslip.line'].browse(max(LON_A_id)).total if LON_A_id else 0.0
    #         total_ls += LS
    #         excel_sheet.write(row, col, LS, base_format)
    #         col += 1
    #         LON_C_id = payslip.line_ids.search([('code', '=', 'sals'), ('slip_id', '=', payslip.id)]).ids
    #         LC = self.env['hr.payslip.line'].browse(max(LON_C_id)).total if LON_C_id else 0.0
    #         total_lc += LC
    #         excel_sheet.write(row, col, LC, base_format)
    #         col += 1
    #         LON_C_id = payslip.line_ids.search([('code', '=', ''), ('slip_id', '=', payslip.id)]).ids
    #         Lz = self.env['hr.payslip.line'].browse(max(LON_C_id)).total if LON_C_id else 0.0
    #         total_lz += Lz
    #         excel_sheet.write(row, col, Lz, base_format)
    #         col += 1
    #         ABS_id = payslip.line_ids.search([('code', '=', 'deda'), ('slip_id', '=', payslip.id)]).ids
    #         ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
    #         total_abs += ABS
    #         excel_sheet.write(row, col, ABS, base_format)
    #         col += 1
    #         LATE_id = payslip.line_ids.search([('code', '=', 'LATE'), ('slip_id', '=', payslip.id)]).ids
    #         LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
    #         total_late += LATE
    #         excel_sheet.write(row, col, LATE, base_format)
    #         col += 1
    #         BREAKFAST_id = payslip.line_ids.search([('code', '=', 'DED'), ('slip_id', '=', payslip.id)]).ids
    #         BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
    #         total_breakfast += BREAKFAST
    #         excel_sheet.write(row, col, BREAKFAST, base_format)
    #         col += 1
    #         TOT_ID = payslip.line_ids.search([('code', '=', 'TOT'), ('slip_id', '=', payslip.id)]).ids
    #         TOT = self.env['hr.payslip.line'].browse(max(TOT_ID)).total if TOT_ID else 0.0
    #         total_tot += TOT
    #         excel_sheet.write(row, col, TOT, base_format)
    #         col += 1
    #         NET_id = payslip.line_ids.search([('code', '=', 'NET'), ('slip_id', '=', payslip.id)]).ids
    #         NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0
    #         total_net += NET
    #         excel_sheet.write(row, col, NET, base_format)
    #         col += 1

    #         col = 0
    #         row += 1
    #         counter += 1

    #     row +=1 
    #     col = 0
    #     excel_sheet.merge_range(row, col, row, col + 2, 'Total', header_format)
    #     col + 1

    #     excel_sheet.write(row, col + 3, total_payslip,header_format)
    #     excel_sheet.write(row, col + 4, total_bouns_wage,header_format)
    #     excel_sheet.write(row, col + 5, total,header_format)
    #     excel_sheet.write(row, col + 6, total_si,header_format)
    #     excel_sheet.write(row, col + 7, total_ls,header_format)
    #     excel_sheet.write(row, col + 8, total_lc,header_format)
    #     excel_sheet.write(row, col + 9, total_lz,header_format)
    #     excel_sheet.write(row, col + 10, total_abs,header_format)
    #     excel_sheet.write(row, col + 11, total_late,header_format)
    #     excel_sheet.write(row, col + 12, total_breakfast,header_format)
    #     excel_sheet.write(row, col + 13, total_tot,header_format)
    #     excel_sheet.write(row, col + 14, total_net,header_format)





    #     workbook.close()
    #     file_download = base64.b64encode(fp.getvalue())
    #     fp.close()
    #     wizardmodel = self.env['employee.payslip.report.excel']
    #     res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
    #     return {
    #         'name': 'Files to Download',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'employee.payslip.report.excel',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'res_id': res_id.id,
    #     }
