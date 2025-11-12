# -*- coding: utf-8 -*-
{
    'name': 'Auto Annual Leave After One Year',
    'version': '1.0',
    'depends': ['hr', 'hr_holidays'],
    'author': 'Iatl-intellisoft',
    'category': 'Human Resources',
    'summary': 'Automatically grant annual leave after 1 year of service',
    'data': [
        'data/cron.xml',
        # 'views/hr_leave.xml'
    ],
    'installable': True,
    'auto_install': False,
}
