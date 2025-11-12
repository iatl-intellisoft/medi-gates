# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrSalaryRule(models.Model):
    """"""
    _inherit = "hr.salary.rule"

    # use_type = fields.Selection(selection_add=[('loan', 'Loan')])
