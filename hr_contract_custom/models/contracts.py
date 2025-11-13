# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, AccessError, ValidationError
from dateutil.relativedelta import relativedelta


class Contracts(models.Model):
    _inherit = 'hr.contract'



    employee_grade = fields.Selection([
        ('m3', 'M3'),
        ('m2', 'M2'),
        ('m1', 'M1'),
        ('p3', 'P3'),
        ('p2', 'P2'),
        ('p1', 'P1'),
        ('s3', 'S3'),
        ('s2', 'S2'),
        ('s1', 'S1')
    ], string='Grade',
        track_visibility='onchange', default='m3', store='True')
    currency_id_usd = fields.Many2one('res.currency', string='Currency USD')

    usd_salary = fields.Float(string='USD Salary', store=True)
    manager_insentive = fields.Float(string="Manager's Insentive SDG", store=True)


  