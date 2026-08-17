# -*- coding: utf-8 -*-
{
    'name': 'Custom Cash Flow Statement',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom Cash Flow Statement (Indirect Method) pulled automatically from the General Ledger',
    'description': """
Custom Cash Flow Statement
===========================
Generates a Cash Flow Statement (indirect method) with the exact line items
requested by the client, computed automatically from posted journal entries
(account.move.line), based on Account Tags assigned to the Chart of Accounts.

Menu: Accounting > Reporting > Custom Cash Flow Statement
""",
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tag_data.xml',
        'wizard/cash_flow_wizard_view.xml',
        'report/cash_flow_report.xml',
        'report/cash_flow_report_template.xml',
    ],
    'installable': True,
    'application': False,
}
