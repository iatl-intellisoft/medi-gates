# -*- coding: utf-8 -*-
{
    'name': 'Sales Monthly Appraisal',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Appraisals',
    'summary': 'Monthly KPI appraisal for the Sales team with Collection & Deduction linked to Accounting',
    'description': """
Sales Monthly Appraisal
========================
Custom monthly appraisal workflow for the Sales team, built around the
KPI structure defined in the "Appraisal May 2026 - Sales" sheet:

* Quantitative Indicators (Number of Visits, Customer Visit Frequency)
* Administrative Tasks (Sales Policy Accuracy, Planning & Organizing,
  Customer Data Update)
* Guarantee Collection (Collection without deduction)
* Applying Deduction Value (Deductive Collection)

Key features
------------
* Configurable KPI categories & KPI definitions (weights, evaluator, max rate)
* Monthly appraisal record per salesperson with KPI lines
* Final Rate = MIN(SUM(KPI rates), Max Total Rate) -- default cap 2%
* Automatic "Total Collected" computed from reconciled customer payments
* Monthly Collection Target per salesperson with Achievement %
* Payout Amount = Total Collected x Final Rate
* Split security: Sales (e.g. Osman) edits all KPIs except the Deduction
  section; Accounting (e.g. Yazeed) edits only the Deduction section
* Draft -> Sales Review -> Accounting Review -> Approved -> Done workflow
* Monthly cron to auto-generate draft appraisals for active salespeople
""",
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr', 'account', 'sales_team'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/kpi_category_data.xml',
        'data/kpi_definition_data.xml',
        'data/cron_data.xml',
        'data/sequence_data.xml',
        'views/sales_appraisal_kpi_category_views.xml',
        'views/sales_appraisal_kpi_definition_views.xml',
        'views/sales_appraisal_target_views.xml',
        'views/sales_appraisal_views.xml',
        'views/sales_appraisal_incentive_views.xml',
        'wizard/sales_appraisal_incentive_report_wizard_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
