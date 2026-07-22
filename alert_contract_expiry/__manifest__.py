{
    'name': 'alert contract expiry', 
    'depends': [
        'hr',
        'mail',
    ],
    'data': [
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/hr_employee_views.xml',
    ]
}