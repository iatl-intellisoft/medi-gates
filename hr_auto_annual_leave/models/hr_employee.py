from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    

    service_years = fields.Integer(compute='_compute_service_years', store=True)

    @api.depends('contract_id.date_start')
    def _compute_service_years(self):
        for emp in self:
            if emp.contract_id.date_start:
                emp.service_years = max(0, (fields.Date.today() - emp.contract_id.date_start).days // 365)
            else:
                emp.service_years = 0

    @api.model
    def allocate_annual_leave_one_year(self):
        today = fields.Date.today()
        # employees = self.search([
        #     ('contract_id.date_start', '!=', False, 'contract_id.state', '=', 'open'),
        # ])
        employees = self.search([
            ('contract_id.date_start', '!=', False),
            ('contract_id.state', '=', 'open'),
        ])

        annual_leave_type = self.env['hr.leave.type'].search([
            ('name', '=', 'Annual Leave')
        ], limit=1)

        if not annual_leave_type:
            raise ValueError("Leave Type 'Annual Leave' not found.")

        for emp in employees:
            date_start = emp.contract_id.date_start
            if date_start and date_start <= (today - timedelta(days=365)):
                # Check if already granted this year
                existing_alloc = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', emp.id),
                    ('holiday_status_id', '=', annual_leave_type.id),
                    ('state', 'in', ['validate', 'confirm']),
                    ('create_date', '>=', fields.Date.to_string(today.replace(month=1, day=1))),
                ])

                if not existing_alloc:
                    self.env['hr.leave.allocation'].create({
                        'name': 'Auto Annual Leave',
                        'employee_id': emp.id,
                        'holiday_status_id': annual_leave_type.id,
                        'number_of_days': 25,
                        'state': 'confirm',
                        # 'mode': 'add',
                    })

    # @api.model
    # def create(self, vals):
    #     # Get Maternity Leave type
    #     maternity_leave_type = self.env['hr.leave.type'].search([
    #         ('name', 'ilike', 'Maternity Leave')
    #     ], limit=1)

    #     if not maternity_leave_type:
    #         raise ValidationError("Maternity Leave type not found. Please create one.")

    #     # If the leave type is Maternity Leave, perform validation
    #     if vals.get('holiday_status_id') == maternity_leave_type.id:
    #         employee = self.env['hr.employee'].browse(vals.get('employee_id'))
    #         if employee.gender != 'female':
    #             raise ValidationError("Only female employees can request Maternity Leave.")

    #         contract_start = employee.contract_id.date_start
    #         if not contract_start:
    #             raise ValidationError("Contract start date not found for this employee.")

    #         today = fields.Date.today()
    #         if contract_start > (today - timedelta(days=180)):
    #             raise ValidationError("Cannot create Maternity Leave because the employee has not completed 6 months of employment.")

    #     # Proceed with normal creation
    #     return super(HrLeave, self).create(vals)


    # @api.model
    # def allocate_maternity_leave(self):
    #     today = fields.Date.today()
    #     employees = self.search([
    #         ('gender', '=', 'female'),
    #         ('contract_id.date_start', '!=', False),
    #     ])

    #     maternity_leave_type = self.env['hr.leave.type'].search([
    #         ('name', 'ilike', 'Maternity Leave')
    #     ], limit=1)

    #     if not maternity_leave_type:
    #         raise ValidationError("Maternity Leave type not found. Please create one.")

    #     for emp in employees:
    #         start_date = emp.contract_id.date_start
    #         if not start_date:
    #             continue

    #         # Check if employee has completed 6 months (180 days)
    #         if start_date <= (today - timedelta(days=180)):
    #             # Avoid duplicate allocation
    #             existing_alloc = self.env['hr.leave.allocation'].search([
    #                 ('employee_id', '=', emp.id),
    #                 ('holiday_status_id', '=', maternity_leave_type.id),
    #                 ('state', 'in', ['validate', 'confirm']),
    #             ])

    #             if not existing_alloc:
    #                 self.env['hr.leave.allocation'].create({
    #                     'name': 'Maternity Leave (Auto)',
    #                     'employee_id': emp.id,
    #                     'holiday_status_id': maternity_leave_type.id,
    #                     'number_of_days': 56,  # 8 weeks
    #                     'state': 'validate',
    #                     'mode': 'add',
    #                 })
