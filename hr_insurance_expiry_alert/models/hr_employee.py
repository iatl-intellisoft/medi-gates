# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api

INSURANCE_ALERT_DAYS = 30


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    insurance_number = fields.Char(
        string='رقم التأمين',
        help='رقم تأمين الموظف (تأمين صحي/اجتماعي).',
        groups='hr.group_hr_user',
        tracking=True,
    )
    insurance_expiry_date = fields.Date(
        string='تاريخ صلاحية التأمين',
        help='يُستخدم هذا التاريخ لإرسال تنبيه إيميل تلقائي قبل %s يومًا من الانتهاء.' % INSURANCE_ALERT_DAYS,
        groups='hr.group_hr_user',
        tracking=True,
    )
    insurance_days_remaining = fields.Integer(
        string='الأيام المتبقية للتأمين',
        compute='_compute_insurance_state',
        groups='hr.group_hr_user',
    )
    insurance_warning_message = fields.Char(
    )
    insurance_state = fields.Selection([
        ('none', 'غير محدد'),
        ('valid', 'ساري'),
        ('expiring', 'قارب على الانتهاء'),
        ('expired', 'منتهي'),
    ], string='حالة التأمين', compute='_compute_insurance_state', store=True, groups='hr.group_hr_user')

    @api.depends('insurance_expiry_date')
    def _compute_insurance_state(self):
        today = fields.Date.context_today(self)
        for employee in self:
            if not employee.insurance_expiry_date:
                employee.insurance_days_remaining = 0
                employee.insurance_state = 'none'
                continue
            delta = (employee.insurance_expiry_date - today).days
            employee.insurance_days_remaining = delta
            if delta < 0:
                employee.insurance_state = 'expired'
            elif delta <= INSURANCE_ALERT_DAYS:
                employee.insurance_state = 'expiring'
            else:
                employee.insurance_state = 'valid'
            if emp.insurance_days_remaining < 0:
                emp.insurance_warning_message = 'منتهي منذ %s يوم' % abs(emp.insurance_days_remaining)        
            else:
                emp.insurance_warning_message = 'متبقي %s يوم' % emp.insurance_days_remaining


    def _get_insurance_alert_recipients(self):
        """ يقرأ عناوين البريد من إعدادات الموظفين، وإن لم تكن محددة
        يستخدم بريد الشركة كحل احتياطي. """
        icp = self.env['ir.config_parameter'].sudo()
        emails = icp.get_param('hr_insurance_expiry_alert.alert_emails')
        if emails:
            return emails
        return self.env.company.email or False

    def _cron_check_insurance_expiry(self):
        today = fields.Date.context_today(self)
        limit_date = today + timedelta(days=INSURANCE_ALERT_DAYS)

        employees = self.sudo().search([
            ('insurance_expiry_date', '!=', False),
            ('insurance_expiry_date', '<=', limit_date),
            ('active', '=', True),
        ], order='insurance_expiry_date asc')

        if not employees:
            return

        recipients = self._get_insurance_alert_recipients()
        if not recipients:
            return  

        rows = []
        for emp in employees:
            if emp.insurance_days_remaining < 0:
                status = 'منتهي منذ %s يوم' % abs(emp.insurance_days_remaining)
                color = '#dc3545'
            else:
                status = 'متبقي %s يوم' % emp.insurance_days_remaining
                color = '#ffc107'
            rows.append("""
                <tr>
                    <td style="padding:6px;border:1px solid #ddd;">%s</td>
                    <td style="padding:6px;border:1px solid #ddd;">%s</td>
                    <td style="padding:6px;border:1px solid #ddd;">%s</td>
                    <td style="padding:6px;border:1px solid #ddd;color:%s;font-weight:bold;">%s</td>
                </tr>
            """ % (
                emp.name or '',
                emp.insurance_number or '-',
                emp.insurance_expiry_date,
                color,
                status,
            ))

        body_html = """
            <p>تنبيه تلقائي: يوجد %s موظف/موظفين بحاجة لمتابعة تأمينهم:</p>
            <table style="border-collapse:collapse;width:100%%;font-family:Arial,sans-serif;font-size:13px;">
                <tr style="background:#f2f2f2;">
                    <th style="padding:6px;border:1px solid #ddd;">الموظف</th>
                    <th style="padding:6px;border:1px solid #ddd;">رقم التأمين</th>
                    <th style="padding:6px;border:1px solid #ddd;">تاريخ الانتهاء</th>
                    <th style="padding:6px;border:1px solid #ddd;">الحالة</th>
                </tr>
                %s
            </table>
        """ % (len(employees), ''.join(rows))

        self.env['mail.mail'].sudo().create({
            'subject': 'تنبيه: تأمين %s موظف يقترب من الانتهاء أو منتهي' % len(employees),
            'email_to': recipients,
            'body_html': body_html,
            'auto_delete': True,
        }).send()
