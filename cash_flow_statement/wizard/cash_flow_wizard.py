# -*- coding: utf-8 -*-
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


# Tags used to link the Chart of Accounts to each line of the report.
# See data/account_tag_data.xml for their definitions.
TAG_DEPRECIATION = 'cash_flow_statement.tag_cf_depreciation'
TAG_GAIN_DISPOSAL = 'cash_flow_statement.tag_cf_gain_on_disposal'
TAG_RECEIVABLES = 'cash_flow_statement.tag_cf_receivables'
TAG_INVENTORIES = 'cash_flow_statement.tag_cf_inventories'
TAG_OTHER_PAYABLES = 'cash_flow_statement.tag_cf_other_payables'
TAG_TAX_ZAKAT = 'cash_flow_statement.tag_cf_tax_zakat'
TAG_PPE_COST = 'cash_flow_statement.tag_cf_ppe_cost'
TAG_DISPOSAL_PROCEEDS = 'cash_flow_statement.tag_cf_disposal_proceeds'
TAG_SHARE_CAPITAL = 'cash_flow_statement.tag_cf_share_capital'
TAG_BORROWINGS = 'cash_flow_statement.tag_cf_borrowings'
TAG_NC_BORROWINGS = 'cash_flow_statement.tag_cf_non_current_borrowings'
TAG_SHAREHOLDER_ACCT = 'cash_flow_statement.tag_cf_shareholder_account'
TAG_CASH = 'cash_flow_statement.tag_cf_cash_equivalents'

INCOME_TYPES = ('income', 'income_other')
EXPENSE_TYPES = ('expense', 'expense_depreciation', 'expense_direct_cost')


class CashFlowStatementWizard(models.TransientModel):
    _name = 'cash.flow.statement.wizard'
    _description = 'Custom Cash Flow Statement Wizard'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    date_from = fields.Date(
        string='Period Start', required=True,
        default=lambda self: fields.Date.context_today(self).replace(month=1, day=1))
    date_to = fields.Date(
        string='Period End', required=True,
        default=fields.Date.context_today)
    include_comparative = fields.Boolean(
        string='Include Comparative Year', default=True,
        help="Also compute the same period one year earlier, "
             "for the second column of the report.")

    # ------------------------------------------------------------------
    # Low level GL helpers
    # ------------------------------------------------------------------
    def _get_tagged_accounts(self, tag_xmlid):
        tag = self.env.ref(tag_xmlid, raise_if_not_found=False)
        if not tag:
            return self.env['account.account']
        return self.env['account.account'].search([('tag_ids', 'in', tag.ids)])

    def _move_lines(self, accounts, date_from=None, date_to=None):
        if not accounts:
            return self.env['account.move.line']
        domain = [
            ('account_id', 'in', accounts.ids),
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
        ]
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        return self.env['account.move.line'].search(domain)

    def _period_flow(self, tag_xmlid, date_from, date_to):
        """Net movement (debit - credit) of tagged accounts strictly
        within the period. Used for P&L add-backs (depreciation,
        gain/loss on disposal) and for period-specific investing
        transactions (PP&E additions, disposal proceeds)."""
        accounts = self._get_tagged_accounts(tag_xmlid)
        lines = self._move_lines(accounts, date_from, date_to)
        return sum(lines.mapped('balance'))

    def _point_balance(self, tag_xmlid, date_to):
        """Cumulative balance (debit - credit) of tagged accounts from
        inception up to and including date_to. Used to get opening /
        closing balances of balance-sheet items."""
        accounts = self._get_tagged_accounts(tag_xmlid)
        lines = self._move_lines(accounts, date_from=None, date_to=date_to)
        return sum(lines.mapped('balance'))

    def _bs_movement(self, tag_xmlid, date_from, date_to):
        """Cash effect of the change in a balance-sheet item during the
        period = opening balance - closing balance (works uniformly for
        assets, liabilities and equity when using the debit-credit
        'balance' convention)."""
        opening = self._point_balance(tag_xmlid, date_from - timedelta(days=1))
        closing = self._point_balance(tag_xmlid, date_to)
        return opening - closing

    # ------------------------------------------------------------------
    # Main computation - returns one dict of every report line for a
    # given period.
    # ------------------------------------------------------------------
    def _compute_period(self, date_from, date_to):
        self.ensure_one()

        pnl_accounts = self.env['account.account'].search([
            ('account_type', 'in', list(INCOME_TYPES + EXPENSE_TYPES)),
        ])
        pnl_lines = self._move_lines(pnl_accounts, date_from, date_to)
        # income accounts are credit-normal (negative 'balance'),
        # expense accounts are debit-normal (positive 'balance'),
        # so profit = -(sum of balances).
        loss_for_period = -sum(pnl_lines.mapped('balance'))

        depreciation = self._period_flow(TAG_DEPRECIATION, date_from, date_to)
        gain_on_disposal = self._period_flow(TAG_GAIN_DISPOSAL, date_from, date_to)

        receivables = self._bs_movement(TAG_RECEIVABLES, date_from, date_to)
        inventories = self._bs_movement(TAG_INVENTORIES, date_from, date_to)
        other_payables = self._bs_movement(TAG_OTHER_PAYABLES, date_from, date_to)
        tax_zakat = self._bs_movement(TAG_TAX_ZAKAT, date_from, date_to)

        operating_before_wc = loss_for_period + depreciation
        cash_from_operations = (
            operating_before_wc + receivables + inventories
            + other_payables + gain_on_disposal + tax_zakat
        )
        net_operating = cash_from_operations

        purchases_ppe = -self._period_flow(TAG_PPE_COST, date_from, date_to)
        proceeds_disposal = -self._period_flow(TAG_DISPOSAL_PROCEEDS, date_from, date_to)
        net_investing = purchases_ppe + proceeds_disposal

        share_capital = self._bs_movement(TAG_SHARE_CAPITAL, date_from, date_to)
        borrowings = self._bs_movement(TAG_BORROWINGS, date_from, date_to)
        non_current_borrowings = self._bs_movement(TAG_NC_BORROWINGS, date_from, date_to)
        shareholder_account = self._bs_movement(TAG_SHAREHOLDER_ACCT, date_from, date_to)
        net_financing = share_capital + borrowings + non_current_borrowings + shareholder_account

        net_movement = net_operating + net_investing + net_financing

        cash_opening = self._point_balance(TAG_CASH, date_from - timedelta(days=1))
        cash_closing = self._point_balance(TAG_CASH, date_to)

        return {
            'date_from': date_from,
            'date_to': date_to,
            'loss_for_period': loss_for_period,
            'depreciation': depreciation,
            'operating_before_wc': operating_before_wc,
            'receivables': receivables,
            'inventories': inventories,
            'other_payables': other_payables,
            'gain_on_disposal': gain_on_disposal,
            'tax_zakat': tax_zakat,
            'cash_from_operations': cash_from_operations,
            'net_operating': net_operating,
            'purchases_ppe': purchases_ppe,
            'proceeds_disposal': proceeds_disposal,
            'net_investing': net_investing,
            'share_capital': share_capital,
            'borrowings': borrowings,
            'non_current_borrowings': non_current_borrowings,
            'shareholder_account': shareholder_account,
            'net_financing': net_financing,
            'net_movement': net_movement,
            'cash_opening': cash_opening,
            'cash_closing_computed': cash_opening + net_movement,
            'cash_closing_actual': cash_closing,
            # Should be ~0. A non-zero variance means an account is
            # missing a "CF - ..." tag, or moved between two tagged
            # accounts without going through the P&L / cash accounts.
            'variance': (cash_opening + net_movement) - cash_closing,
        }

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('cash_flow_statement.action_report_cash_flow_statement').report_action(self)

    def _get_report_data(self):
        """Called by the report parser: current period + optional
        comparative period shifted back exactly one year."""
        self.ensure_one()
        current = self._compute_period(self.date_from, self.date_to)
        comparative = False
        if self.include_comparative:
            comparative = self._compute_period(
                self.date_from - relativedelta(years=1),
                self.date_to - relativedelta(years=1),
            )
        return current, comparative
