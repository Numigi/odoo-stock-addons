# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockWarehouseOrderpoint(models.Model):
    _inherit = ["stock.warehouse.orderpoint", "product.secondary.unit.mixin"]
    _name = "stock.warehouse.orderpoint"

    _secondary_unit_fields = {
        "qty_field": "qty_to_order",
        "uom_field": "product_uom",
    }

    # Store product_uom to be able to groupBy Unit Of Measure
    product_uom = fields.Many2one(store=True)

    # Redefine fields to change String
    secondary_uom_qty = fields.Float(string="To Order 2nd Unit", digits=(16, 2))
    secondary_uom_id = fields.Many2one(
        string="2nd Unit", 
        related="product_id.stock_secondary_uom_id", 
        store=True, 
        readonly=True
    )
    qty_to_order = fields.Float(
        store=True, readonly=False, compute="_compute_qty_to_order", copy=True
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id", "qty_to_order")
    def _compute_qty_to_order(self):
        self._compute_helper_target_field_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    # Add On Hand and forecast in secondary unit
    secondary_uom_on_hand = fields.Float(
        string="On Hand 2nd Unit",
        digits=(16, 2),
        compute="_compute_on_hand_forecast_secondary_uom",
        store=True,
    )

    secondary_uom_forecast = fields.Float(
        string="Forecast 2nd Unit",
        digits=(16, 2),
        compute="_compute_on_hand_forecast_secondary_uom",
        store=True,
    )

    @api.depends("secondary_uom_id", "qty_on_hand", "qty_forecast")
    def _compute_on_hand_forecast_secondary_uom(self):
        """
        Compute the on hand and forecast quantities in secondary unit.
        """
        for line in self:
            if not line.secondary_uom_id:
                line.secondary_uom_on_hand = 0.0
                line.secondary_uom_forecast = 0.0
                continue
            elif line.secondary_uom_id.dependency_type == "independent":
                continue
            factor = line._get_factor_line()
            qty_on_hand = float_round(
                line.qty_on_hand / (factor or 1.0),
                precision_rounding=line.secondary_uom_id.uom_id.rounding,
            )
            qty_forecast = float_round(
                line.qty_forecast / (factor or 1.0),
                precision_rounding=line.secondary_uom_id.uom_id.rounding,
            )
            line.secondary_uom_on_hand = qty_on_hand
            line.secondary_uom_forecast = qty_forecast
