# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    hr_receipt = fields.Boolean("HR Receipt", default=False)

