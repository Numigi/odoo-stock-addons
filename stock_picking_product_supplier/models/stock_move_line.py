# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_supplier_name = fields.Char(
        compute="_compute_product_supplier_name",
        string="Product Supplier Name",
        store=True,
        size=64,
    )

    @api.depends(
        "picking_id.partner_id", "product_id", "product_id.seller_ids.name"
    )
    def _compute_product_supplier_name(self):
        self.write({"product_supplier_name" : False})
        for line in self.filtered(
            lambda l: l.picking_id
            and l.picking_id.partner_id
            and l.product_id.product_tmpl_id.seller_ids
        ):
            suppliers = line.product_id.product_tmpl_id.seller_ids.filtered(
                lambda l: l.name == line.picking_id.partner_id
            )
            if suppliers:
                line.product_supplier_name = suppliers[0].name.name
