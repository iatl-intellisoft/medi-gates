# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class EmergencyRelation(models.Model):
    _name = 'emergency.relation'

    name = fields.Char(string="Name")


class Employee(models.Model):
    """
    A class to contain employee age field
    """
    _inherit = 'hr.employee'

    age = fields.Integer(string="Age", compute='_compute_age', store=False)
    insurance_no = fields.Integer(string="Social Insurance No.")
    emergency_ral = fields.Many2one('emergency.relation', string="Emergency Contact Relation")

    @api.depends('birthday')
    def _compute_age(self):
        """
        A method to calculate employee age
        """
        for employee in self:
            if employee.birthday is not None:
                date = fields.date.today()
                employee.age = relativedelta(date, employee.birthday).years


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    insurance_no = fields.Integer(string="Social Insurance No.")
    emergency_ral = fields.Many2one('emergency.relation', string="Emergency Contact Relation")

