# from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError
#
#
# class HrPayrollBatch(models.Model):
#     _inherit = 'hr.payslip.run'
#
#     def print_pdf(self):
#
#         row = 2
#         col = 0
#
#         excel_sheet.write(row, col, 'رقم', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'الإسم', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'القسم', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'المرتب', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'الحافز', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'الإجمالي', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'ضمان إجتماعي', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'سلفية طويلة', header_format)
#         col += 1
#         excel_sheet.write(row, col, ' نصف راتب وكشوفات', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'غياب', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'تاخير', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'إستقطاعات أخرى ', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'إستقطاع فطور ', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'إجمالي الإسقطاعات ', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'الصافي ', header_format)
#         col += 1
#         excel_sheet.write(row, col, 'التوقيع ', header_format)
#         col += 1
#         # excel_sheet.write(row, col, 'موقوف ', header_format)
#         # col += 1
#
#         col = 0
#         row += 1
#         counter = 1
#         for payslip in self.slip_ids:
#             employee = payslip.employee_id
#
#             excel_sheet.write(row, col, counter, base_format)
#             col += 1
#             excel_sheet.write(row, col, employee.name, base_format)
#             col += 1
#             excel_sheet.write(row, col, employee.department_id.name, base_format)
#             col += 1
#             excel_sheet.write(row, col, payslip.contract_id.wage, base_format)
#             col += 1
#             excel_sheet.write(row, col, payslip.contract_id.bouns_wage, base_format)
#             col += 1
#             excel_sheet.write(row, col, payslip.contract_id.wage + payslip.contract_id.bouns_wage, base_format)
#             col += 1
#             SI_id = payslip.line_ids.search([('code', '=', 'SI'), ('slip_id', '=', payslip.id)]).ids
#             SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
#             excel_sheet.write(row, col, SI, base_format)
#             col += 1
#             LON_A_id = payslip.line_ids.search([('code', '=', 'LOANC'), ('slip_id', '=', payslip.id)]).ids
#             LS = self.env['hr.payslip.line'].browse(max(LON_A_id)).total if LON_A_id else 0.0
#             excel_sheet.write(row, col, LS, base_format)
#             col += 1
#             LON_C_id = payslip.line_ids.search([('code', '=', 'batch'), ('slip_id', '=', payslip.id)]).ids
#             LC = self.env['hr.payslip.line'].browse(max(LON_C_id)).total if LON_C_id else 0.0
#             excel_sheet.write(row, col, LC, base_format)
#             col += 1
#             LON_C_id = payslip.line_ids.search([('code', '=', ''), ('slip_id', '=', payslip.id)]).ids
#             Lz = self.env['hr.payslip.line'].browse(max(LON_C_id)).total if LON_C_id else 0.0
#             excel_sheet.write(row, col, Lz, base_format)
#             col += 1
#             ABS_id = payslip.line_ids.search([('code', '=', 'deda'), ('slip_id', '=', payslip.id)]).ids
#             ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
#             excel_sheet.write(row, col, ABS, base_format)
#             col += 1
#             LATE_id = payslip.line_ids.search([('code', '=', 'LATE'), ('slip_id', '=', payslip.id)]).ids
#             LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
#             excel_sheet.write(row, col, LATE, base_format)
#             col += 1
#             BREAKFAST_id = payslip.line_ids.search([('code', '=', 'DED'), ('slip_id', '=', payslip.id)]).ids
#             BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
#             excel_sheet.write(row, col, BREAKFAST, base_format)
#             col += 1
#             TOT_ID = payslip.line_ids.search([('code', '=', 'TOT'), ('slip_id', '=', payslip.id)]).ids
#             TOT = self.env['hr.payslip.line'].browse(max(TOT_ID)).total if TOT_ID else 0.0
#             excel_sheet.write(row, col, TOT, base_format)
#             col += 1
#             NET_id = payslip.line_ids.search([('code', '=', 'NET'), ('slip_id', '=', payslip.id)]).ids
#             NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0
#             excel_sheet.write(row, col, NET, base_format)
#             col += 1
#
#             col = 0
#             row += 1
#             counter += 1
#
#         workbook.close()
#         file_download = base64.b64encode(fp.getvalue())
#         fp.close()
#         wizardmodel = self.env['employee.payslip.report.excel']
#         res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
#         return {
#             'name': 'Files to Download',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'employee.payslip.report.excel',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'res_id': res_id.id,
#         }
