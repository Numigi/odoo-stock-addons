# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
