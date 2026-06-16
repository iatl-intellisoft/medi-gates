from datetime import timedelta

from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    visa_alert_sent = fields.Boolean(
        string='Visa Alert Sent',
        default=False,
        copy=False
    )

    visa_warning = fields.Boolean(
        compute='_compute_visa_warning'
    )

    visa_warning_message = fields.Char(
        compute='_compute_visa_warning'
    )

    @api.depends('visa_expire')
    def _compute_visa_warning(self):
        today = fields.Date.today()

        for rec in self:
            rec.visa_warning = False
            rec.visa_warning_message = False

            if not rec.visa_expire:
                continue

            if rec.visa_expire <= today:
                rec.visa_warning = True
                rec.visa_warning_message = (
                    'Visa has expired.'
                )

            elif rec.visa_expire <= today + timedelta(days=21):
                rec.visa_warning = True
                rec.visa_warning_message = (
                    'Visa will expire within 21 days.'
                )

    def write(self, vals):
        res = super().write(vals)

        if 'visa_expire' in vals:
            self.write({
                'visa_alert_sent': False
            })

        return res

    @api.model
    def cron_visa_expiry_alert(self):

        target_date = (
            fields.Date.today()
            + timedelta(days=21)
        )

        employees = self.search([
            ('visa_expire', '=', target_date),
            ('visa_alert_sent', '=', False),
        ])

        template = self.env.ref(
            'passpord_visa_alert.email_template_visaa'
        )

        hr_users = self.env.ref(
            'hr.group_hr_user'
        ).users.filtered(
            lambda u: u.partner_id.email
        )

        for employee in employees:

            recipients = hr_users

            if (
                employee.parent_id
                and employee.parent_id.user_id
                and employee.parent_id.user_id.partner_id.email
            ):
                recipients |= employee.parent_id.user_id

            for user in recipients:
                template.send_mail(
                    employee.id,
                    email_values={
                        'email_to': user.partner_id.email,
                    },
                    force_send=True
                )

            employee.visa_alert_sent = True 

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
