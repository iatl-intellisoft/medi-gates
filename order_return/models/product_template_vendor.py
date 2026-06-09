from odoo import api, fields, models


class ProductTemplateVendor(models.Model):
    _inherit = 'product.template'

    
    first_vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        compute='_compute_first_vendor_id',
        store=True,  
    )

    @api.depends(
        'seller_ids',
        'seller_ids.partner_id',
        'seller_ids.sequence',   
    )
    def _compute_first_vendor_id(self):
        for product in self:
            
            first_seller = product.seller_ids.sorted('sequence')[:1]
            product.first_vendor_id = first_seller.partner_id if first_seller else False


class ProductSupplierInfoVendor(models.Model):
    _inherit = 'product.supplierinfo'

    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._recompute_product_vendor()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'sequence' in vals or 'partner_id' in vals:
            self._recompute_product_vendor()
        return res

    def unlink(self):
        products = self.mapped('product_tmpl_id')
        res = super().unlink()
        products._compute_first_vendor_id()
        return res

    def _recompute_product_vendor(self):
        """إعادة حساب first_vendor_id على المنتجات المرتبطة"""
        products = self.mapped('product_tmpl_id')
        products._compute_first_vendor_id()