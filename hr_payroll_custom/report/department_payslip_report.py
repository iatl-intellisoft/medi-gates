# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools, _
from odoo.tools import float_round
from odoo.exceptions import UserError
from datetime import datetime,date


class DepartmentPayslipReport(models.AbstractModel):
    _name = 'report.hr_payroll_custom.department_payslip_temp'

    def _get_header_info(self, data):
        from_date = data['from_date']
        to_date = data['to_date']
        department_id = data['department_id'] 
        department_name = data['department_name'] 
        company_id = data['comp']


        return {
            'from_date': from_date,
            'to_date': to_date,
            'department_id': department_id,
            'department_name': department_name ,
            'company_id': company_id,

        }
    

    def _get_report(self, data):
        list_data =[]
        if data['from_date'] > data['to_date']:
            raise UserError(_("You must be enter start date less than end date."))


        domain = [('slip_id.date_from','>=',data['from_date']),
                ('slip_id.date_to','<=',data['to_date']),
                ('slip_id.company_id','=',data['comp']),
                ]
                # ('slip_id.state','=','paid')

        payslips = self.env['hr.payslip.line'].search(domain)

        if data['department_id'] and data['from_date'] and data['to_date'] :
            list_data = []
            domain.append(('slip_id.department_id','=',data['department_id']))
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@",domain)
            net_rule = 0
            currency_id = ''
            for payslip in payslips.search(domain):
                if payslip.code == 'NET':
                    currency_id = payslip.currency_id.symbol
                    net_rule += payslip.total
            list_data.append({
                'currency_id': currency_id,
                'amount': net_rule
            })
            return list_data
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@", list_data)

        if not data['department_id'] and data['from_date'] and data['to_date']:
            list_data = []
            
            for dep in self.env['hr.department'].search([]):
                net_rule = 0
                currency_id = ''
                name = dep.name

                for line in payslips.filtered(lambda r:r.slip_id.department_id == dep):
                    if line.code == 'NET':
                        net_rule += line.total
                        currency_id = line.currency_id.symbol

                list_data.append({
                    'name': name,
                    'currency_id' : currency_id,
                    'amount': net_rule
                })
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@list_data", list_data)

            return list_data



        
    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['hr.payslip'].browse(data)
        docs = data['records']
        payslip_report = self.env['ir.actions.report']._get_report_from_name('hr_payroll_custom.department_payslip_temp')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': payslip_report.model,
            'docs': data,
            'get_header': self._get_header_info(data),
            'get_report': self._get_report(data),
        }