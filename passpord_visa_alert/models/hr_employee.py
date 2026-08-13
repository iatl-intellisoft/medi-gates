from datetime import timedelta

from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    insurance_expiry_date = fields.Date(
        string="Insurance Expiration Date",
        store=True
    )
    insurance_warning = fields.Boolean(
        compute='_compute_insurance_warning',
        store=False,
    )
    insurance_warning_message = fields.Text(
        compute='_compute_insurance_warning',
        store=False,
    )
    visa_warning = fields.Boolean(
        compute='_compute_visa_warning',
        store=False,
    )
    visa_warning_message = fields.Text(
        compute='_compute_visa_warning',
        store=False,
    )
    @api.depends('insurance_expiry_date')
    def _compute_insurance_warning(self):
        today = fields.Date.today()

        for employee in self:
            employee.insurance_warning = False
            employee.insurance_warning_message = False
            if not employee.insurance_expiry_date:
                continue
            insurance_days_left = (employee.insurance_expiry_date - today).days

            if insurance_days_left < 0:
                employee.insurance_warning = True
                employee.insurance_warning_message = (
                    f'Employee insurance expired on {employee.insurance_expiry_date}'
                )

            elif insurance_days_left <= 15:
                employee.insurance_warning = True
                employee.insurance_warning_message = (
                    f'Employee insurance will expire after {insurance_days_left} day(s) '
                    f'on {employee.insurance_expiry_date}'
                )


    @api.depends('visa_expire')
    def _compute_visa_warning(self):
        today = fields.Date.today()

        for employee in self:
            employee.visa_warning = False
            employee.visa_warning_message = False
            if not employee.visa_expire:
                continue

            visa_days_left = (employee.visa_expire - today).days 

            if visa_days_left < 0:
                employee.visa_warning = True
                employee.visa_warning_message = (
                    f'Employee visa expired on {employee.visa_expire}'
                )

            elif visa_days_left <= 15:
                employee.visa_warning = True
                employee.visa_warning_message = (
                    f'Employee visa will expire after {visa_days_left} day(s) '
                    f'on {employee.visa_expire}'
                )


    # visa_alert_sent = fields.Boolean(
    #     string='Visa Alert Sent',
    #     default=False,
    #     copy=False
    # )

    # visa_warning = fields.Boolean(
    #     compute='_compute_visa_warning'
    # )

    # visa_warning_message = fields.Char(
    #     compute='_compute_visa_warning'
    # )

    # @api.depends('visa_expire')
    # def _compute_visa_warning(self):
    #     today = fields.Date.today()

    #     for rec in self:
    #         rec.visa_warning = False
    #         rec.visa_warning_message = False

    #         if not rec.visa_expire:
    #             continue

    #         if rec.visa_expire <= today:
    #             rec.visa_warning = True
    #             rec.visa_warning_message = (
    #                 'Visa has expired.'
    #             )

    #         elif rec.visa_expire <= today + timedelta(days=21):
    #             rec.visa_warning = True
    #             rec.visa_warning_message = (
    #                 'Visa will expire within 21 days.'
    #             )

    # def write(self, vals):
    #     res = super().write(vals)

    #     if 'visa_expire' in vals:
    #         self.write({
    #             'visa_alert_sent': False
    #         })

    #     return res

    # @api.model
    # def cron_visa_expiry_alert(self):

    #     target_date = (
    #         fields.Date.today()
    #         + timedelta(days=21)
    #     )

    #     employees = self.search([
    #         ('visa_expire', '=', target_date),
    #         ('visa_alert_sent', '=', False),
    #     ])

    #     template = self.env.ref(
    #         'passpord_visa_alert.email_template_visaa'
    #     )

    #     hr_users = self.env.ref(
    #         'hr.group_hr_user'
    #     ).users.filtered(
    #         lambda u: u.partner_id.email
    #     )

    #     for employee in employees:

    #         recipients = hr_users

    #         if (
    #             employee.parent_id
    #             and employee.parent_id.user_id
    #             and employee.parent_id.user_id.partner_id.email
    #         ):
    #             recipients |= employee.parent_id.user_id

    #         for user in recipients:
    #             template.send_mail(
    #                 employee.id,
    #                 email_values={
    #                     'email_to': user.partner_id.email,
    #                 },
    #                 force_send=True
    #             )

    #         employee.visa_alert_sent = True 

    # passport_warning = fields.Boolean(
    #     compute='_compute_passport_warning'
    # )

    # passport_warning_message = fields.Char(
    #     compute='_compute_passport_warning'
    # )

    # @api.depends('passport_expiration_date')
    # def _compute_passport_warning(self):

    #     today = fields.Date.today()

    #     for rec in self:

    #         rec.passport_warning = False
    #         rec.passport_warning_message = False

    #         if not rec.passport_expiration_date:
    #             continue

    #         if rec.passport_expiration_date <= today:
    #             rec.passport_warning = True
    #             rec.passport_warning_message = (
    #                 "Passport has expired."
    #             )

    #         elif rec.passport_expiration_date <= today + timedelta(days=21):
    #             rec.passport_warning = True
    #             rec.passport_warning_message = (
    #                 "Passport will expire within 21 days."
    #             )

    # def cron_passport_expiry_alert(self):

    #     today = fields.Date.today()
    #     target_date = today + timedelta(days=21)

    #     employees = self.search([
    #         ('passport_expiration_date', '=', target_date)
    #     ])

    #     template = self.env.ref(
    #         'passpord_visa_alert.email_template_passport_expiry'
    #     )

    #     hr_group = self.env.ref(
    #         'hr.group_hr_user'
    #     )

    #     hr_users = hr_group.user_ids.filtered(
    #         lambda u: u.partner_id.email
    #     )

    #     for employee in employees:

    #         recipients = hr_users

    #         if employee.parent_id \
    #                 and employee.parent_id.user_id:
    #             recipients |= employee.parent_id.user_id

    #         for user in recipients:
    #             template.send_mail(
    #                 employee.id,
    #                 email_values={
    #                     'email_to':
    #                         user.partner_id.email
    #                 },
    #                 force_send=True
                # )
