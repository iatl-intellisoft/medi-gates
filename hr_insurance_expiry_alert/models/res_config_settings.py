# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_insurance_alert_emails = fields.Char(
        string='بريد تنبيه انتهاء التأمين',
        config_parameter='hr_insurance_expiry_alert.alert_emails',
        help='عناوين بريد إلكتروني (مفصولة بفاصلة) تستقبل تنبيهًا يوميًا بالموظفين '
             'الذين تنتهي صلاحية تأمينهم خلال 30 يومًا أو أقل. إن تركته فارغًا '
             'سيُستخدم البريد الإلكتروني للشركة.',
    )
