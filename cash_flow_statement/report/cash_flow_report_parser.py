# -*- coding: utf-8 -*-
from odoo import api, models


class CashFlowStatementReport(models.AbstractModel):
    _name = 'report.cash_flow_statement.report_cash_flow_statement_document'
    _description = 'Custom Cash Flow Statement Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizards = self.env['cash.flow.statement.wizard'].browse(docids)
        results = []
        for wizard in wizards:
            current, comparative = wizard._get_report_data()
            results.append({
                'wizard': wizard,
                'current': current,
                'comparative': comparative,
            })
        return {
            'doc_ids': docids,
            'doc_model': 'cash.flow.statement.wizard',
            'docs': wizards,
            'reports': results,
        }
