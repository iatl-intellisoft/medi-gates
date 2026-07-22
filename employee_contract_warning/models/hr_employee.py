from datetime import timedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_warning = fields.Boolean(
        compute='_compute_contract_warning',
        store=False,
    )

    contract_warning_message = fields.Text(
        compute='_compute_contract_warning',
        store=False,
    )

    @api.depends('contract_ids.date_end', 'contract_ids.state')
    def _compute_contract_warning(self):
        today = fields.Date.today()

        for employee in self:
            employee.contract_warning = False
            employee.contract_warning_message = False

            contract = self.env['hr.contract'].search(
                [
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open'),
                    ('date_end', '!=', False),
                ],
                order='date_end desc',
                limit=1,
            )

            if not contract:
                continue

            days_left = (contract.date_end - today).days

            if days_left < 0:
                employee.contract_warning = True
                employee.contract_warning_message = (
                    f'Employee contract expired on {contract.date_end}'
                )

            elif days_left <= 21:
                employee.contract_warning = True
                employee.contract_warning_message = (
                    f'Employee contract will expire after {days_left} day(s) '
                    f'on {contract.date_end}'
                )