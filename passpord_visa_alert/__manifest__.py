{
    'name': 'Passport Expiry Alert', 
    'depends': ['hr','mail'],
    'data': [
        'data/mail_template_passport.xml',
        'data/mail_template_visa.xml',
        'data/ir_cron.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
}