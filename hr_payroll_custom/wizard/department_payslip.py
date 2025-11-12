# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DepartmentPayslipWizard(models.TransientModel):
    _name = 'department.payslip'
    _description = "Department Payslip Report"

    from_date  = fields.Date(string='From')
    to_date = fields.Date(string='To')
    department_id = fields.Many2one('hr.department',string="Department")
    company_id = fields.Many2one('res.company', string='Company', required=True,default=lambda self: self.env.company)



    def print_report(self):
        data = {}

        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['department_id'] = self.department_id.id
        data['department_name'] = self.department_id.name
        data['comp'] = self.company_id.id

        return self.env.ref('hr_payroll_custom.department_payslip_id').report_action([], data=data)


