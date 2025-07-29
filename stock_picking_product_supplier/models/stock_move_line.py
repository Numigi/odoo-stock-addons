# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_supplier_code = fields.Char(
        compute="_compute_product_supplier_code",
        string="Product Supplier Code",
        store=True,
        size=64,
    )

    @api.depends(
        "picking_id.partner_id", "product_id", "product_id.seller_ids.product_code"
    )
    def _compute_product_supplier_code(self):
        for line in self:
            line.product_supplier_code = False
            partner = line.picking_id.partner_id
            if partner and line.product_id.product_tmpl_id.seller_ids:
                suppliers = line.product_id.product_tmpl_id.seller_ids.filtered(
                    lambda s: s.name == partner
                )
                if suppliers:
                    line.product_supplier_code = suppliers[0].product_code
