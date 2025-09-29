

{
    'name': ' Kambal Payroll Module',
    'author': 'IATL-IntelliSoft Software',
    'website': 'http://www.intellisoft.sd',
    'category': 'Human Resources',
    'images': [],
    'summary': '',
    'description': """ """,

    'depends': ['hr','hr_payroll','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # 'wizard/employee_payslip_report.xml',
        # 'wizard/payslip_report_pdf_view.xml',
        # 'wizard/department_payslip_view.xml',
        'views/hr_payslip_view.xml',
        # 'report/department_payslip_view.xml',
        # 'report/payslip_report_pdf_view.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

