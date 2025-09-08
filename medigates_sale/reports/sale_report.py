
from odoo import models, fields, api

class SaleInvoiceReport2(models.Model):
    _name = 'sale.invoice.report2'
    _description = 'Sales Invoice Financial Report'
    _auto = False  # computed (read-only) model

    partner_id = fields.Many2one('res.partner', string="Customer")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    city = fields.Char(string="City")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_amount = fields.Monetary(string="Invoice Value (SDG)", currency_field='currency_id')
    payment_term = fields.Many2one('account.payment.term', string="Payment Term")
    payment_value = fields.Monetary(string="Payment Value", currency_field='currency_id')
    total_due = fields.Monetary(string="Total Due", currency_field='currency_id')
    overdue_value = fields.Monetary(string="Overdue Value", currency_field='currency_id')
    not_past_due = fields.Monetary(string="Not Past Due Value", currency_field='currency_id')
    commitment_rate = fields.Float(string="Payment Term Commitment (%)")
    currency_id = fields.Many2one('res.currency', string='Currency')
    sale_order_name = fields.Char(string="Sale Order Number")




    def _select(self):
	    return """
	        SELECT
	            row_number() OVER () AS id,
	            inv.partner_id,
	            so.warehouse_id,
	            rp.city,
	            inv.id AS invoice_id,
	            inv.invoice_date,
	            inv.amount_total AS invoice_amount,
	            so.payment_term_id AS payment_term,
	            (inv.amount_total - inv.amount_residual) AS payment_value,
	            inv.amount_residual AS total_due,
	            CASE WHEN inv.invoice_date_due < CURRENT_DATE THEN inv.amount_residual ELSE 0 END AS overdue_value,
	            CASE WHEN inv.invoice_date_due >= CURRENT_DATE THEN inv.amount_residual ELSE 0 END AS not_past_due,
	            CASE WHEN inv.amount_total > 0 THEN ROUND(((inv.amount_total - inv.amount_residual) / inv.amount_total) * 100, 2) ELSE 0 END AS commitment_rate,
	            inv.currency_id,
	            so.name AS sale_order_name
	    """



    def _from(self):
	    return """
	        FROM account_move inv
	        JOIN res_partner rp ON inv.partner_id = rp.id
	        LEFT JOIN sale_order so ON so.name = inv.invoice_origin
	        WHERE inv.move_type = 'out_invoice' AND inv.state = 'posted'
	    """


    def init(self):
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._select()}
                {self._from()}
            )
        """)
