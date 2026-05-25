from odoo import api, fields, models


class ProductTemplateVendor(models.Model):
    _inherit = 'product.template'
 
    first_vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        compute='_compute_first_vendor_id',
        store=True,
    )

    @api.depends('seller_ids', 'seller_ids.partner_id', 'seller_ids.sequence')
    def _compute_first_vendor_id(self):
        for product in self: 
            first_seller = product.seller_ids[:1]
            product.first_vendor_id = first_seller.partner_id if first_seller else False
