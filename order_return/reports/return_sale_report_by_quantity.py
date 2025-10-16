# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE


class SaleReturnReportQuanitiy(models.Model):
    _name = "order.return.report.quanitiy"
    _description = "Sales Return Analysis Report"
    _auto = False
    _rec_name = 'return_date'
    _order = 'return_date desc'

    @api.model
    def _get_done_states(self):
        return ['sale']

    # sale.order fields
    return_name = fields.Char(string="Order Reference", readonly=True)
    order_reference = fields.Many2one('order.return', string='Order Reference', readonly=True)

    return_date = fields.Date(string="Order Date", readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer", readonly=True)
    company_id = fields.Many2one(comodel_name='res.company', readonly=True)
    pricelist_id = fields.Many2one(comodel_name='product.pricelist', readonly=True)
    team_id = fields.Many2one(comodel_name='crm.team', string="Sales Team", readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string="Salesperson", readonly=True)
    state = fields.Selection(selection=SALE_ORDER_STATE, string="Status", readonly=True)
    invoice_status = fields.Selection(
        selection=[
            ('upselling', "Upselling Opportunity"),
            ('invoiced', "Fully Invoiced"),
            ('to invoice', "To Invoice"),
            ('no', "Nothing to Invoice"),
        ], string="Order Invoice Status", readonly=True)

    campaign_id = fields.Many2one(comodel_name='utm.campaign', string="Campaign", readonly=True)
    medium_id = fields.Many2one(comodel_name='utm.medium', string="Medium", readonly=True)
    source_id = fields.Many2one(comodel_name='utm.source', string="Source", readonly=True)

    # res.partner fields
    commercial_partner_id = fields.Many2one(
        comodel_name='res.partner', string="Customer Entity", readonly=True)
    country_id = fields.Many2one(
        comodel_name='res.country', string="Customer Country", readonly=True)
    industry_id = fields.Many2one(
        comodel_name='res.partner.industry', string="Customer Industry", readonly=True)
    partner_zip = fields.Char(string="Customer ZIP", readonly=True)
    state_id = fields.Many2one(comodel_name='res.country.state', string="Customer State", readonly=True)

    categ_id = fields.Many2one(
        comodel_name='product.category', string="Product Category", readonly=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string="Product Variant", readonly=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string="Product", readonly=True)
    product_uom = fields.Many2one(comodel_name='uom.uom', string="Unit of Measure", readonly=True)
    # product_uom_qty = fields.Float(string="Qty Ordered", readonly=True)
    
    # sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    ordered_qty = fields.Float(string="Ordered Quantity", readonly=True)
    returned_qty = fields.Float(string="Returned Quantity", readonly=True)
    remaining_qty = fields.Float(string="Remaining Quantity", readonly=True)

    line_invoice_status = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('posted', "Posted"),
            
        ], string="Invoice Status", readonly=True)
    payment_state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('paid,', "Paid"),
            
        ], string="Invoice Status", readonly=True)

    price_unit = fields.Float(string="Unit Price", aggregator='avg', readonly=True)
    discount = fields.Float(string="Discount %", readonly=True, aggregator='avg')
    discount_amount = fields.Monetary(string="Discount Amount", readonly=True)

    invoice_date = fields.Datetime(string="Invoice Date", readonly=True)
    city = fields.Char(related='partner_id.city', string='Customer City')
    location_id = fields.Many2one('stock.location', string="Return Location", tracking=True, )
    product_bonus_uom_qty = fields.Float(string="Bonus Qty returned", readonly=True)


    # aggregates or computed fields
    nbr = fields.Integer(string="# of Lines", readonly=True)
    currency_id = fields.Many2one(comodel_name='res.currency', compute='_compute_currency_id')
    city = fields.Char(related='partner_id.city', string='Customer City')
    invoice_number = fields.Char(string='Invoice Number')
    sale_id_reference = fields.Char(related='order_reference.origin', string='Source Document')
    lot_numbers = fields.Char(string="Lot Numbers", readonly=True)




    @api.depends_context('allowed_company_ids')
    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    def _with_sale(self):
        return """
        s.state = 'done'
        AND am.state = 'posted'
        AND am.payment_state = 'paid'
        """

    def _select_sale(self):
        select_ = f"""
            MIN(l.id) AS id,
            l.product_id AS product_id,
            t.uom_id AS product_uom,
            CASE WHEN l.price_unit = 0 THEN SUM(l.qty_return) ELSE 0 END AS product_bonus_uom_qty,
            so_line.product_uom_qty AS ordered_qty,
            SUM(l.qty_return) AS returned_qty,
            (so_line.product_uom_qty - SUM(l.qty_return)) AS remaining_qty,

            l.price_unit AS price_unit,
            u.id AS line_uom_id,
            u.factor AS line_uom_factor,
            u2.id AS template_uom_id,
            u2.factor AS template_uom_factor,
            COUNT(*) AS nbr,
            s.id AS order_reference,
            s.name AS return_name,
            s.return_date AS return_date,
            s.state AS state,
            so.invoice_status as invoice_status,
            s.partner_id AS partner_id,
            so.user_id AS user_id,
            s.company_id AS company_id,
            so.campaign_id AS campaign_id,
            so.medium_id AS medium_id,
            so.source_id AS source_id,
            t.categ_id AS categ_id,
            so.pricelist_id AS pricelist_id,
            so.team_id AS team_id,
            p.product_tmpl_id,
            partner.commercial_partner_id AS commercial_partner_id,
            partner.country_id AS country_id,
            partner.industry_id AS industry_id,
            partner.state_id AS state_id,
            partner.zip AS partner_zip,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(p.weight * l.qty_return / u.factor * u2.factor) ELSE 0 END AS weight,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(p.volume * l.qty_return / u.factor * u2.factor) ELSE 0 END AS volume,
            l.discount AS discount,
            CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_unit * l.qty_return * l.discount / 100.0
                / {self._case_value_or_one('so.currency_rate')}
                * {self._case_value_or_one('account_currency_table.rate')}
                ) ELSE 0
            END AS discount_amount,
            s.location_id AS location_id,
            am.invoice_date AS invoice_date,
            am.name AS invoice_number,
            am.state AS line_invoice_status,
            am.payment_state AS payment_state,
            concat('order.return', ',', s.id) AS name,

            STRING_AGG(lot.name, ', ') AS lot_numbers
        """

        additional_fields_info = self._select_additional_fields()
        template = """,
            %s AS %s"""
        for fname, query_info in additional_fields_info.items():
            select_ += template % (query_info, fname)

        return select_

    def _case_value_or_one(self, value):
        return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""

    def _select_additional_fields(self):
        """Hook to return additional fields SQL specification for select part of the table query."""
        return {}

    def _from_sale(self):
        currency_table = self.env['res.currency']._get_simple_currency_table(self.env.companies)
        currency_table = self.env.cr.mogrify(currency_table).decode(self.env.cr.connection.encoding)
        return f"""
            order_return_line l
            LEFT JOIN order_return s ON s.id = l.return_id
            LEFT JOIN sale_order so ON so.id = s.sale_id
            LEFT JOIN sale_order_line so_line ON so_line.order_id = s.sale_id AND so_line.product_id = l.product_id
            LEFT JOIN account_move am ON am.return_order_id = s.id
            JOIN res_partner partner ON s.partner_id = partner.id
            LEFT JOIN product_product p ON l.product_id = p.id
            LEFT JOIN product_template t ON p.product_tmpl_id = t.id
            LEFT JOIN uom_uom u ON u.id = l.product_uom
            LEFT JOIN uom_uom u2 ON u2.id = t.uom_id
            LEFT JOIN stock_move_line sml ON sml.picking_id = s.sale_picking_id AND sml.product_id = l.product_id
            LEFT JOIN stock_lot lot ON sml.lot_id = lot.id
            JOIN {currency_table} ON account_currency_table.company_id = s.company_id
        """

    # def _where_sale(self):
    #     return """
    #     s.state = 'done'
    #     AND am.state = 'posted'
    #     AND am.payment_state = 'paid'
    #     """

    def _where_sale(self):
        return """
            s.state = 'done'
            AND am.state = 'posted'
        """

    def _group_by_sale(self):
        return """
            l.product_id,
            l.return_id,
            l.price_unit,
            l.qty_return,
            t.uom_id,
            t.categ_id,
            s.name,
            s.return_date,
            s.partner_id,
            so.user_id,
            s.state,
            so.campaign_id,
            so.medium_id,
            so.invoice_status,
            s.company_id,
            so.source_id,
            so.pricelist_id,
            so.team_id,
            p.product_tmpl_id,
            partner.commercial_partner_id,
            partner.country_id,
            partner.industry_id,
            partner.state_id,
            partner.zip,
            l.discount,
            s.id,
            s.location_id,
            so_line.product_uom_qty,
            u.id,
            u2.id,
            u.factor,
            u2.factor,
            am.invoice_date,
            am.name,
            am.state,
            am.payment_state,
            account_currency_table.rate"""

    # def _query(self):
    #     with_ = self._with_sale()
    #     return f"""
    #         {"WITH" + with_ + "(" if with_ else ""}
    #         SELECT {self._select_sale()}
    #         FROM {self._from_sale()}
    #         WHERE {self._where_sale()}
    #         GROUP BY {self._group_by_sale()}
    #         {")" if with_ else ""}
    #     """

    def _query(self):
        return f"""
            SELECT {self._select_sale()}
            FROM {self._from_sale()}
            WHERE {self._where_sale()}
            GROUP BY {self._group_by_sale()}
        """

    @property
    def _table_query(self):
        return self._query()

    def action_open_order(self):
        self.ensure_one()
        return {
            'res_model': self.order_reference._name,
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'res_id': self.order_reference.id,
        }
