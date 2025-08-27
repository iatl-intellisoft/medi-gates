from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # @api.model
    # def create(self, vals):
    #     self._check_paternity_restriction(vals)
    #     return super().create(vals)

    # def write(self, vals):
    #     self._check_paternity_restriction(vals)
    #     return super().write(vals)

    # def _check_paternity_restriction(self, vals):
    #     leave_type_id = vals.get('holiday_status_id')
    #     employee_id = vals.get('employee_id')

    #     # Use current record if not set in vals
    #     for leave in self:
    #         if not leave_type_id:
    #             leave_type_id = leave.holiday_status_id.id
    #         if not employee_id:
    #             employee_id = leave.employee_id.id

    #         leave_type = self.env['hr.leave.type'].browse(leave_type_id)
    #         employee = self.env['hr.employee'].browse(employee_id)

    #         if leave_type.name.lower() == 'paternity leave':
    #             if employee.gender != 'male' or employee.marital != 'married':
    #                 raise ValidationError(
    #                     _("Only married male employees are eligible for Paternity Leave.")
    #                 )

class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'


    @api.model
    def create(self, vals):
        self._check_maternity_eligibility(vals)
        self._check_paternity_restriction(vals)
        return super().create(vals)

    def write(self, vals):
        self._check_maternity_eligibility(vals)
        self._check_paternity_restriction(vals)
        return super().write(vals)

    def _check_maternity_eligibility(self, vals):
        leave_type_id = vals.get('holiday_status_id')
        employee_id = vals.get('employee_id')

        # Allow update if it's not maternity or missing info
        if not leave_type_id or not employee_id:
            return

        leave_type = self.env['hr.leave.type'].browse(leave_type_id)
        employee = self.env['hr.employee'].browse(employee_id)

        # Check only for maternity leave
        if 'maternity' in leave_type.name.lower():
            if employee.gender != 'female':
                raise ValidationError(_("Only female employees are eligible for Maternity Leave."))

            start_date = employee.contract_id.date_start
            if not start_date:
                raise ValidationError(_("Contract start date is missing. Cannot validate eligibility."))

            if start_date > fields.Date.today() - timedelta(days=180):
                raise ValidationError(_("Maternity Leave is only available after 6 months of continuous service."))
            # else:
            #     # Set number_of_days_display to 56 days (8 weeks)
            #     self.number_of_days_display = 56.0
    


    def _check_paternity_restriction(self, vals):
        leave_type_id = vals.get('holiday_status_id')
        employee_id = vals.get('employee_id')

        # Use current record if not set in vals
        for leave in self:
            if not leave_type_id:
                leave_type_id = leave.holiday_status_id.id
            if not employee_id:
                employee_id = leave.employee_id.id

            leave_type = self.env['hr.leave.type'].browse(leave_type_id)
            employee = self.env['hr.employee'].browse(employee_id)

            if leave_type.name.lower() == 'paternity leave':
                if employee.gender != 'male' or employee.marital != 'married':
                    raise ValidationError(
                        _("Only married male employees are eligible for Paternity Leave.")
                    )
    
    @api.constrains('holiday_status_id', 'number_of_days_display')
    def _check_maternity_leave_days(self):
        maternity_leave_type = self.env['hr.leave.type'].search([
            ('name', 'ilike', 'Maternity Leave')
        ], limit=1)

        for leave in self:
            if maternity_leave_type and leave.holiday_status_id.id == maternity_leave_type.id:
                if leave.number_of_days_display != 56:
                    raise ValidationError("Maternity Leave must be exactly 56 days (4 weeks before and 4 weeks after delivery).")

    
    @api.constrains('holiday_status_id', 'number_of_days_display')
    def _check_paternity_leave_days(self):
        paternity_leave_type = self.env['hr.leave.type'].search([
            ('name', 'ilike', 'Paternity Leave')
        ], limit=1)

        for leave in self:
            if paternity_leave_type and leave.holiday_status_id.id == paternity_leave_type.id:
                if leave.number_of_days_display != 1:
                    raise ValidationError("Paternity Leave must be exactly 1 day.")

    # @api.constrains('holiday_status_id', 'date_from', 'date_to')
    # def _check_vacation_request_rules(self):
    #     for leave in self:
    #         # Only apply this policy to Annual Leave
    #         if leave.holiday_status_id.name.lower() != 'annual leave':
    #             continue

    #         # Advance notice rules
    #         leave_duration = (leave.date_to - leave.date_from).days + 1
    #         today = fields.Date.today()

    #         if leave_duration >= 5:
    #             if (leave.date_from - today).days < 7:
    #                 raise ValidationError("Vacation requests of 5 days or more must be submitted at least 1 week in advance.")
    #         else:
    #             if (leave.date_from - today).days < 3:
    #                 raise ValidationError("Vacation requests of fewer than 5 days must be submitted at least 3 days in advance.")

    #         # Probation rules
    #         employee = leave.employee_id
    #         contract = employee.contract_id
    #         if contract and contract.date_start:
    #             days_worked = (leave.date_from - contract.date_start).days
    #             total_accrued = (25 * days_worked) / 365
    #             if employee.employee_type == 'trainee':
    #                 if leave.number_of_days > total_accrued:
    #                     raise ValidationError("Vacation during probation may not exceed accrued amount. Excess will be unpaid.")

    # @api.model
    # def accrue_annual_vacation(self):
    #     """
    #     Called by a cron job on Jan 1st to add vacation days to all employees.
    #     """
    #     today = fields.Date.today()
    #     if today:
    #         employees = self.env['hr.employee'].search([])
    #         annual_leave_type = self.env['hr.leave.type'].search([('name', 'ilike', 'Annual Leave')], limit=1)

    #         if not annual_leave_type:
    #             raise ValidationError("Annual Leave type not found.")

    #         for emp in employees:
    #             if not emp.contract_id.date_start:
    #                 continue

    #             # Skip if employee was on unpaid leave all year
    #             unpaid_days = self.env['hr.leave'].search_count([
    #                 ('employee_id', '=', emp.id),
    #                 ('holiday_status_id.unpaid', '=', True),
    #                 ('date_from', '>=', f'{today.year - 1}-01-01'),
    #                 ('date_to', '<=', f'{today.year - 1}-12-31')
    #             ])
    #             if unpaid_days > 200:
    #                 continue  # Consider as not eligible

    #             years = emp.service_years
    #             if years == 0:
    #                 days = 25 * ((today - emp.contract_id.date_start).days / 365)
    #             else:
    #                 days = min(25 + years, 30)  # Max 30 days

    #             # Carryover: no more than 2 years of entitlement
    #             max_balance = min(30, 25 + years) * 2

    #             # Check existing allocation
    #             current_alloc = self.env['hr.leave.allocation'].search([
    #                 ('employee_id', '=', emp.id),
    #                 ('holiday_status_id', '=', annual_leave_type.id),
    #                 ('state', '=', 'validate')
    #             ])

    #             total_existing_days = sum(current_alloc.mapped('number_of_days'))
    #             carryover_days = min(total_existing_days, max_balance)

    #             # Allocate only if under max
    #             new_days = min(days, max_balance - carryover_days)

    #             if new_days > 0:
    #                 self.env['hr.leave.allocation'].create({
    #                     'name': f'Annual Leave Credit {today.year}',
    #                     'employee_id': emp.id,
    #                     'holiday_status_id': annual_leave_type.id,
    #                     'number_of_days': new_days,
    #                     'state': 'confirm',
    #                     # 'mode': 'add',
    #                 })

    # @api.model
    # def accrue_annual_vacation(self):
    #     """
    #     Accrues annual vacation days for employees.
    #     Runs typically on Jan 1st, but allows manual execution for testing.
    #     Rules:
    #     - 25 days for the first year.
    #     - +1 day for each year of service.
    #     - Max vacation per year = 30 days.
    #     - Total balance (including carryover) cannot exceed 30 days.
    #     """
    #     today = fields.Date.today()
    #     employees = self.env['hr.employee'].search([])
    #     annual_leave_type = self.env['hr.leave.type'].search([('name', 'ilike', 'Annual Leave')], limit=1)

    #     if not annual_leave_type:
    #         raise ValidationError("Annual Leave type not found.")

    #     for emp in employees:
    #         contract_start = emp.contract_id.date_start
    #         if not contract_start:
    #             continue  # Skip employees without contract start date

    #         # Skip if employee was on unpaid leave all year
    #         unpaid_days = self.env['hr.leave'].search_count([
    #             ('employee_id', '=', emp.id),
    #             ('holiday_status_id.unpaid', '=', True),
    #             ('date_from', '>=', f'{today.year - 1}-01-01'),
    #             ('date_to', '<=', f'{today.year - 1}-12-31')
    #         ])
    #         if unpaid_days > 200:
    #             continue  # Considered inactive

    #         # Compute years of service
    #         years_of_service = (today - contract_start).days // 365

    #         # Determine vacation days for this year
    #         yearly_vacation = min(25 + years_of_service, 30)

    #         # Compute total validated allocations (carryover)
    #         validated_allocations = self.env['hr.leave.allocation'].search([
    #             ('employee_id', '=', emp.id),
    #             ('holiday_status_id', '=', annual_leave_type.id),
    #             ('state', '=', 'validate')
    #         ])
    #         current_total = sum(validated_allocations.mapped('number_of_days'))

    #         # Determine how much more can be allocated (to not exceed 30)
    #         available_to_allocate = max(0, 30 - current_total)

    #         if available_to_allocate > 0:
    #             allocation_amount = min(yearly_vacation, available_to_allocate)

    #             self.env['hr.leave.allocation'].create({
    #                 'name': f'Annual Leave Credit {today.year}',
    #                 'employee_id': emp.id,
    #                 'holiday_status_id': annual_leave_type.id,
    #                 'number_of_days': allocation_amount,
    #                 'state': 'confirm',  # Use 'validate' if you want it automatically approved
    #                 'allocation_type': 'regular',
    #             })
# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import datetime
# import logging

# _logger = logging.getLogger(__name__)

# class HrLeave(models.Model):
#     _inherit = 'hr.leave'

    @api.model
    def accrue_annual_vacation(self):
        """
        Accrues annual vacation days for employees once per year.
        Prevents duplicate allocations by checking existing ones for the current year.
        """
        today = fields.Date.today()
        current_year = today.year
        employees = self.env['hr.employee'].search([])
        annual_leave_type = self.env['hr.leave.type'].search([('name', 'ilike', 'Annual Leave')], limit=1)

        if not annual_leave_type:
            raise ValidationError("Annual Leave type not found.")

        for emp in employees:
            contract_start = emp.contract_id.date_start
            if not contract_start:
                continue

            existing_allocation = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', emp.id),
                ('holiday_status_id', '=', annual_leave_type.id),
                ('date_from', '>=', f'{current_year}-01-01'),
                ('date_from', '<=', f'{current_year}-12-31'),
                ('state', 'in', ['confirm', 'validate']),
            ], limit=1)

            if existing_allocation:
                _logger.info(f"Skipping {emp.name} — already has allocation for {current_year}")
                continue

            # Skip if unpaid leave > 200 days in previous year
            unpaid_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('holiday_status_id.unpaid', '=', True),
                ('date_from', '>=', f'{current_year - 1}-01-01'),
                ('date_to', '<=', f'{current_year - 1}-12-31')
            ])
            unpaid_days = sum(leave.number_of_days for leave in unpaid_leaves)
            if unpaid_days > 200:
                _logger.info(f"Skipping {emp.name} — over 200 unpaid leave days in {current_year - 1}")
                continue

            # Calculate years of service
            years_of_service = (today - contract_start).days // 365

            # Determine base allocation (based on policy)
            base_allocation = min(25 + (current_year - 2025), 30) if current_year >= 2025 else 0

            # Adjust by years of service (max 30)
            final_allocation = min(max(base_allocation, 25 + years_of_service), 30)

            # Create the allocation
            self.env['hr.leave.allocation'].create({
                'name': f'Annual Leave {current_year}',
                'employee_id': emp.id,
                'holiday_status_id': annual_leave_type.id,
                'number_of_days': final_allocation,
                'date_from': date(current_year, 1, 1),
                'date_to': date(current_year, 12, 31),
                'state': 'confirm',
                'allocation_type': 'regular',
            })

            _logger.info(f"Allocated {final_allocation} days to {emp.name} for {current_year}")


            # Prevent duplicate allocation for the year
            # existing_allocation = self.env['hr.leave.allocation'].search([
            #     ('employee_id', '=', emp.id),
            #     ('holiday_status_id', '=', annual_leave_type.id),
            #     ('date_from', '>=', f'{today.year}-01-01'),
            #     ('date_from', '<=', f'{today.year}-12-31'),
            #     ('state', 'in', ['confirm', 'validate']),
            # ], limit=1)

            # if existing_allocation:
            #     _logger.info(f"Skipping {emp.name} — already has allocation for {today.year}")
            #     continue

            # # Skip if unpaid leave over 200 days
            # unpaid_days = self.env['hr.leave'].search_count([
            #     ('employee_id', '=', emp.id),
            #     ('holiday_status_id.unpaid', '=', True),
            #     ('date_from', '>=', f'{today.year - 1}-01-01'),
            #     ('date_to', '<=', f'{today.year - 1}-12-31')
            # ])
            # if unpaid_days > 200:
            #     continue

            # years_of_service = (today - contract_start).days // 365
            # yearly_vacation = min(25 + years_of_service, 30)

            # validated_allocations = self.env['hr.leave.allocation'].search([
            #     ('employee_id', '=', emp.id),
            #     ('holiday_status_id', '=', annual_leave_type.id),
            #     ('state', '=', 'validate')
            # ])
            # current_total = sum(validated_allocations.mapped('number_of_days'))

            # available_to_allocate = max(0, 30 - current_total)

            # if available_to_allocate > 0:
            #     allocation_amount = min(yearly_vacation, available_to_allocate)

            #     self.env['hr.leave.allocation'].create({
            #         'name': f'Annual Leave Credit {today.year}',
            #         'employee_id': emp.id,
            #         'holiday_status_id': annual_leave_type.id,
            #         'number_of_days': allocation_amount,
            #         'date_from': date(today.year, 1, 1),
            #         'date_to': date(today.year, 12, 31),
            #         'state': 'confirm',
            #         'allocation_type': 'regular',
            #     })

            #     _logger.info(f"Allocated {allocation_amount} days to {emp.name} for {today.year}")

