# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_secondary_unit_qty = fields.Float(
        string="2nd Unit On Hand Qty",
        compute="compute_secondary_unit_qty",
        digits="Product Unit of Measure",
        store=True,
    )
    available_secondary_unit_qty = fields.Float(
        string="2nd Unit Available Qty",
        compute="compute_secondary_unit_qty",
        digits="Product Unit of Measure",
        store=True,
    )
    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="2nd Unit",
        related="product_tmpl_id.stock_secondary_uom_id",
        store=True,
    )

    @api.depends(
        "stock_secondary_uom_id",
        "inventory_quantity",
        "available_quantity",
        "product_uom_id.rounding",
    )
    def compute_secondary_unit_qty(self):
        if self.user_has_groups("stock.group_stock_manager"):
            self = self.with_context(inventory_mode=True)
        for line in self:
            inventory_qty = 0.0
            available_qty = 0.0
            if line.stock_secondary_uom_id:
                inventory_qty = line.inventory_quantity / (
                    line.stock_secondary_uom_id.factor or 1.0
                )
                available_qty = line.available_quantity / (
                    line.stock_secondary_uom_id.factor or 1.0
                )
                inventory_qty = float_round(
                    inventory_qty, precision_rounding=line.product_uom_id.rounding
                )
                available_qty = float_round(
                    available_qty, precision_rounding=line.product_uom_id.rounding
                )
            line.write(
                {
                    "inventory_secondary_unit_qty": inventory_qty,
                    "available_secondary_unit_qty": available_qty,
                }
            )
