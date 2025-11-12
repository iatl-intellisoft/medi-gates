# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools, _
from odoo.tools import float_round
from odoo.exceptions import UserError
from datetime import datetime,date


class DepartmentPayslipReport(models.AbstractModel):
    _name = 'report.hr_payroll_custom.payslip_report_pdf_temp'

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


        domain = [('date_from','>=',data['from_date']),
                ('date_to','<=',data['to_date']),
                ('company_id','=',data['comp']),
                ('state','=','verify')]


        payslips = self.env['hr.payslip'].search(domain)

        if data['department_id'] and data['from_date'] and data['to_date'] :
            list_data = []
            manger_data = []
            employees = self.env['hr.employee'].search([('department_id','=',data['department_id'])])

            total_wage = 0.0
            total_bouns = 0.0
            total_si = 0.0
            total_med_ins = 0.0
            half_wage = 0.0
            total_loan = 0.0
            total_abs = 0.0
            total_late = 0.0
            total_breakfast = 0.0
            total_ded = 0.0
            total_net = 0.0
            total = 0
            for emp in employees:
                if emp == emp.department_id.manager_id:
                    pay = payslips.filtered(lambda r: r.employee_id == emp)

                    # if payslip:
                    total_wage = pay.contract_id.wage
                    print("_______________________________total_wage",total_wage)
                    total_bouns =  pay.contract_id.bouns
                    #

                    SI_id = pay.line_ids.search([('code','=','SI'),('slip_id','=',pay.id)]).ids
                    SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
                    total_si = SI

                    MED_INS_id = pay.line_ids.search([('code','=','MED_INS'),('slip_id','=',pay.id)]).ids
                    MED_INS = self.env['hr.payslip.line'].browse(max(MED_INS_id)).total if MED_INS_id else 0.0
                    total_med_ins += MED_INS
                    
                    half_wage+= pay.contract_id.wage/2

                    total_loan = pay.search([('id','=',pay.id)]).total_amount_paid
                    # 

                    ABS_id = pay.line_ids.search([('code','=','ABS'),('slip_id','=',pay.id)]).ids
                    ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
                    total_abs = ABS

                    LATE_id = pay.line_ids.search([('code','=','LATE'),('slip_id','=',pay.id)]).ids
                    LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
                    total_late = LATE

                    BREAKFAST_id = pay.line_ids.search([('code','=','BREAKFAST'),('slip_id','=',pay.id)]).ids
                    BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
                    total_breakfast = BREAKFAST

                    total_ded = total_si + total_med_ins + total_loan + total_abs + total_late + total_breakfast

                    NET_id = pay.line_ids.search([('code','=','NET'),('slip_id','=',pay.id)]).ids
                    NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0          
                    total_net = NET

                    total = total_wage + total_bouns


                    manger_data.append({
                        'emp_name':emp.name,
                        'total_wage': total_wage,
                        'total_bouns': total_bouns,
                        'total': total,
                        'total_si': total_si,
                        # 'total_med_ins': total_med_ins,
                        # 'half_wage': half_wage,
                        'total_loan': total_loan,
                        'total_abs':total_abs,
                        'total_late': total_late,
                        'total_breakfast': total_breakfast,
                        'total_ded':total_ded,
                        'total_net': total_net,

                    })

                else:

                    pay = payslips.filtered(lambda r: r.employee_id == emp)

                    # if payslip:
                    total_wage = pay.contract_id.wage
                    print("_______________________________total_wage",total_wage)
                    total_bouns = pay.contract_id.bouns

                    # 
                    SI_id = pay.line_ids.search([('code','=','SI'),('slip_id','=',pay.id)]).ids
                    SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
                    total_si = SI

                    MED_INS_id = pay.line_ids.search([('code','=','MED_INS'),('slip_id','=',pay.id)]).ids
                    MED_INS = self.env['hr.payslip.line'].browse(max(MED_INS_id)).total if MED_INS_id else 0.0
                    total_med_ins += MED_INS
                    
                    half_wage+= pay.contract_id.wage/2

                    total_loan = pay.search([('id','=',pay.id)]).total_amount_paid
                    # 

                    ABS_id = pay.line_ids.search([('code','=','ABS'),('slip_id','=',pay.id)]).ids
                    ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
                    total_abs = ABS

                    LATE_id = pay.line_ids.search([('code','=','LATE'),('slip_id','=',pay.id)]).ids
                    LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
                    total_late = LATE

                    BREAKFAST_id = pay.line_ids.search([('code','=','BREAKFAST'),('slip_id','=',pay.id)]).ids
                    BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
                    total_breakfast = BREAKFAST

                    total_ded = total_si + total_med_ins + total_loan + total_abs + total_late + total_breakfast

                    NET_id = pay.line_ids.search([('code','=','NET'),('slip_id','=',pay.id)]).ids
                    NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0          
                    total_net = NET

                    total = total_wage + total_bouns


                    list_data.append({
                        'emp_name':emp.name,
                        'total_wage': total_wage,
                        'total_bouns': total_bouns,
                        'total': total,
                        'total_si': total_si,
                        # 'total_med_ins': total_med_ins,
                        # 'half_wage': half_wage,
                        'total_loan': total_loan,
                        'total_abs':total_abs,
                        'total_late': total_late,
                        'total_breakfast': total_breakfast,
                        'total_ded':total_ded,
                        'total_net': total_net,

                    })
            return [list_data ,manger_data]
            

        if not data['department_id'] and data['from_date'] and data['to_date']:
            list_data = []
            manger_data = []
            
            for dep in self.env['hr.department'].search([]):
                net_rule = 0
                currency_id = ''
                name_dep = dep.name

                emp_data = []
                
                employees = self.env['hr.employee'].search([('department_id','=',dep.id)])

                total_wage = 0.0
                total_bouns = 0.0
                total_si = 0.0
                total_med_ins = 0.0
                half_wage = 0.0
                total_loan = 0.0
                total_abs = 0.0
                total_late = 0.0
                total_breakfast = 0.0
                total_ded = 0.0
                # total_sale_lone = 0.0
                total_long_lone = 0.0
                total_net = 0.0
                total = 0
                for emp in employees:
                    
                    if emp == dep.manager_id :
                        print("*******************************88",dep.manager_id, emp)
                        pay = payslips.filtered(lambda r: r.employee_id == emp)
                        print("**************************pay",pay)


                        # if payslip:
                        total_wage = pay.contract_id.wage
                        print("_______________________________total_wage",total_wage)
                        total_bouns = pay.contract_id.bouns
                        # 

                        SI_id = pay.line_ids.search([('code','=','SI'),('slip_id','=',pay.id)]).ids
                        SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
                        total_si = SI

                        MED_INS_id = pay.line_ids.search([('code','=','MED_INS'),('slip_id','=',pay.id)]).ids
                        MED_INS = self.env['hr.payslip.line'].browse(max(MED_INS_id)).total if MED_INS_id else 0.0
                        total_med_ins += MED_INS
                        
                        half_wage+= pay.contract_id.wage/2

                        # total_loan = pay.search([('id','=',pay.id)]).total_amount_paid
                        

                        ABS_id = pay.line_ids.search([('code','=','ABS'),('slip_id','=',pay.id)]).ids
                        ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
                        total_abs = ABS

                        LATE_id = pay.line_ids.search([('code','=','LATE'),('slip_id','=',pay.id)]).ids
                        LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
                        total_late = LATE

                        BREAKFAST_id = pay.line_ids.search([('code','=','BREAKFAST'),('slip_id','=',pay.id)]).ids
                        BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
                        total_breakfast = BREAKFAST

                        sale_lone = pay.line_ids.search([('code', '=', 'sals'), ('slip_id', '=', pay.id)]).ids
                        salelones = self.env['hr.payslip.line'].browse(max(sale_lone)).total if sale_lone else 0.0
                        print("_______________________________________salelones",salelones)

                        total_sale_lone = salelones

                        long_lone = pay.line_ids.search([('code', '=', 'LOANC'), ('slip_id', '=', pay.id)]).ids
                        longlones = self.env['hr.payslip.line'].browse(max(long_lone)).total if long_lone else 0.0
                        print("_______________________________________longlones",longlones)
                        total_long_lone = longlones

                        total_ded = total_si + total_med_ins + total_long_lone + total_abs + total_late + total_breakfast + total_sale_lone

                        NET_id = pay.line_ids.search([('code','=','NET'),('slip_id','=',pay.id)]).ids
                        NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0          
                        total_net = NET

                        total = total_wage + total_bouns


                        manger_data.append({
                            'emp_name':emp.name,
                            'total_wage': total_wage,
                            'total_bouns': total_bouns,
                            'total': total,
                            'total_si': total_si,
                            # 'total_med_ins': total_med_ins,
                            # 'half_wage': half_wage,
                            # 'total_loan': total_loan,
                            'total_long_lone': total_long_lone,
                            'total_sale_lone': total_sale_lone,
                            'total_abs':total_abs,
                            'total_late': total_late,
                            'total_breakfast': total_breakfast,
                            'total_ded':total_ded,
                            'total_net': total_net,

                        })



                    else:

                        pay = payslips.filtered(lambda r: r.employee_id == emp)
                        print("**************************pay",pay)


                        # if payslip:
                        total_wage = pay.contract_id.wage
                        print("_______________________________total_wage",total_wage)
                        total_bouns = pay.contract_id.bouns
                        # 

                        SI_id = pay.line_ids.search([('code','=','SI'),('slip_id','=',pay.id)]).ids
                        SI = self.env['hr.payslip.line'].browse(max(SI_id)).total if SI_id else 0.0
                        total_si = SI

                        MED_INS_id = pay.line_ids.search([('code','=','MED_INS'),('slip_id','=',pay.id)]).ids
                        MED_INS = self.env['hr.payslip.line'].browse(max(MED_INS_id)).total if MED_INS_id else 0.0
                        total_med_ins += MED_INS
                        
                        half_wage+= pay.contract_id.wage/2

                        # total_loan = pay.search([('id','=',pay.id)]).total_amount_paid
                        

                        ABS_id = pay.line_ids.search([('code','=','ABS'),('slip_id','=',pay.id)]).ids
                        ABS = self.env['hr.payslip.line'].browse(max(ABS_id)).total if ABS_id else 0.0
                        total_abs = ABS

                        LATE_id = pay.line_ids.search([('code','=','LATE'),('slip_id','=',pay.id)]).ids
                        LATE = self.env['hr.payslip.line'].browse(max(LATE_id)).total if LATE_id else 0.0
                        total_late = LATE

                        BREAKFAST_id = pay.line_ids.search([('code','=','BREAKFAST'),('slip_id','=',pay.id)]).ids
                        BREAKFAST = self.env['hr.payslip.line'].browse(max(BREAKFAST_id)).total if BREAKFAST_id else 0.0
                        total_breakfast = BREAKFAST

                        sale_lone = pay.line_ids.search([('code', '=', 'sals'), ('slip_id', '=', pay.id)]).ids
                        salelones = self.env['hr.payslip.line'].browse(max(sale_lone)).total if sale_lone else 0.0
                        print("_______________________________________salelones",salelones)

                        total_sale_lone = salelones

                        long_lone = pay.line_ids.search([('code', '=', 'LOANC'), ('slip_id', '=', pay.id)]).ids
                        longlones = self.env['hr.payslip.line'].browse(max(long_lone)).total if long_lone else 0.0
                        print("_______________________________________longlones",longlones)
                        total_long_lone = longlones

                        total_ded = total_si + total_med_ins + total_long_lone + total_abs + total_late + total_breakfast + total_sale_lone

                        NET_id = pay.line_ids.search([('code','=','NET'),('slip_id','=',pay.id)]).ids
                        NET = self.env['hr.payslip.line'].browse(max(NET_id)).total if NET_id else 0.0          
                        total_net = NET

                        total = total_wage + total_bouns


                        emp_data.append({
                            'emp_name':emp.name,
                            'total_wage': total_wage,
                            'total_bouns': total_bouns,
                            'total': total,
                            'total_si': total_si,
                            # 'total_med_ins': total_med_ins,
                            # 'half_wage': half_wage,
                            # 'total_loan': total_loan,
                            'total_long_lone': total_long_lone,
                            'total_sale_lone': total_sale_lone,
                            'total_abs':total_abs,
                            'total_late': total_late,
                            'total_breakfast': total_breakfast,
                            'total_ded':total_ded,
                            'total_net': total_net,

                        })

                list_data.append({
                    'name': name_dep,
                    'emp_data': emp_data,
                 
                })
            return [list_data ,manger_data]

        
    @api.model
    def _get_report_values(self, docids, data=None):
        data['records'] = self.env['hr.payslip'].browse(data)
        docs = data['records']
        payslip_report = self.env['ir.actions.report']._get_report_from_name('hr_payroll_custom.payslip_report_pdf_temp')
        docargs = {

            'data': data,
            'docs': docs,
        }
        return {
            'doc_ids': self.ids,
            'doc_model': payslip_report.model,
            'docs': data,
            'get_header': self._get_header_info(data),
            'get_report': self._get_report(data)[0],
            'manger_data': self._get_report(data)[1],
        }