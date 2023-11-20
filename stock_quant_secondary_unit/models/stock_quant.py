# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    secondary_unit_qty_available = fields.Float(
        string="2nd Unit On Hand Qty",
        compute="compute_secondary_unit_qty_available",
        digits="Product Unit of Measure",
        store=True,
    )
    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="2nd Unit",
        related="product_tmpl_id.stock_secondary_uom_id",
        store=True,
    )

    available_second_unit = fields.Float(
        string="Available 2nd Unit",
        compute="compute_available_second_unit",
        digits="Product Unit of Measure",
        store=True,
    )

    @api.depends(
        "stock_secondary_uom_id", "inventory_quantity", "product_uom_id.rounding"
    )
    def compute_secondary_unit_qty_available(self):
        if self.user_has_groups("stock.group_stock_manager"):
            self = self.with_context(inventory_mode=True)
        for stock_quant_line in self:
            if not stock_quant_line.stock_secondary_uom_id:
                stock_quant_line.secondary_unit_qty_available = 0.0
            else:
                qty = stock_quant_line.inventory_quantity / (
                    stock_quant_line.stock_secondary_uom_id.factor or 1.0
                )
                val = float_round(
                    qty, precision_rounding=stock_quant_line.product_uom_id.rounding
                )
                stock_quant_line.write({"secondary_unit_qty_available": val})

    @api.depends("stock_secondary_uom_id", "available_quantity")
    def compute_available_second_unit(self):
        if self.user_has_groups("stock.group_stock_manager"):
            self = self.with_context(inventory_mode=True)
        for stock_quant_line in self:
            if not stock_quant_line.stock_secondary_uom_id:
                stock_quant_line.available_second_unit = 0.0
            else:
                qty = stock_quant_line.available_quantity / (
                    stock_quant_line.stock_secondary_uom_id.factor or 1.0
                )
                val = float_round(
                    qty, precision_rounding=stock_quant_line.product_uom_id.rounding
                )
                stock_quant_line.write({"available_second_unit": val})

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(StockQuant, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=False
        )
        if view_type != "tree":
            return res

        if view_type == "tree":
            tree_view_id = self.env["ir.model.data"].xmlid_to_res_id(
                "stock.view_stock_quant_tree_editable"
            )
            if res.get("view_id") == tree_view_id:
                doc = etree.XML(res["arch"])
                for field in res["fields"]:
                    for node in doc.xpath("//field[@name='%s']" % field):
                        node.set("optional", "show")
                res["arch"] = etree.tostring(doc, encoding="unicode")

                return res
