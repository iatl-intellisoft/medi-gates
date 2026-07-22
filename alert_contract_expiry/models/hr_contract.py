from datetime import timedelta

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_alert_sent = fields.Boolean(
        string='Contract Alert Sent',
        default=False,
        copy=False
    )

    contract_warning = fields.Boolean(
        compute='_compute_contract_warning'
    )

    contract_warning_message = fields.Char(
        compute='_compute_contract_warning'
    )

    @api.depends('date_end')
    def _compute_contract_warning(self):
        today = fields.Date.today()

        for rec in self:
            rec.contract_warning = False
            rec.contract_warning_message = False

            # if not rec.date_end:
            #     continue

            if rec.date_end <= today:
                rec.contract_warning = True
                rec.contract_warning_message = (
                    'Contract has expired.'
                )

            elif rec.date_end <= today + timedelta(days=21):
                rec.contract_warning = True
                rec.contract_warning_message = (
                    'Contract will expire within 21 days.'
                )

    def write(self, vals):
        res = super().write(vals)

        if 'date_end' in vals:
            self.write({
                'contract_alert_sent': False
            })

        return res

    @api.model
    def cron_contract_expiry_alert(self):

        target_date = (
            fields.Date.today()
            + timedelta(days=21)
        )

        contracts = self.search([
            ('date_end', '=', target_date),
            ('contract_alert_sent', '=', False),
        ])

        template = self.env.ref(
            'alert_contract_expiry.email_template_contract_expiry'
        )

        hr_users = self.env.ref(
            'hr.group_hr_user'
        ).users.filtered(
            lambda u: u.partner_id.email
        )

        for contract in contracts:

            recipients = hr_users

            if (
                contract.parent_id
                and contract.parent_id.user_id
                and contract.parent_id.user_id.partner_id.email
            ):
                recipients |= contract.parent_id.user_id

            for user in recipients:
                template.send_mail(
                    contract.id,
                    email_values={
                        'email_to': user.partner_id.email,
                    },
                    force_send=True
                )

            contract.contract_alert_sent = True