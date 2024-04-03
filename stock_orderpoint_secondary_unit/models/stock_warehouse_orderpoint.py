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

    # This field is using the mixin field to calculate the secondary unit quantity
    # for the qty_to_order field.
    secondary_uom_qty = fields.Float(
        string="To Order 2nd Unit",
        digits="Product Unit of Measure",
        inverse="_inverse_secondary_uom_qty",
    )

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="2nd Unit",
        ondelete="restrict",
        related="product_tmpl_id.stock_secondary_uom_id",
        store=True,
    )

    secondary_uom_qty_on_hand = fields.Float(
        string="On Hand Qty 2nd Unit",
        digits="Product Unit of Measure",
        compute="_compute_to_secondary_uom",
        store=True,
    )

    secondary_uom_qty_forecast = fields.Float(
        string="Forecast 2nd Unit",
        digits="Product Unit of Measure",
        compute="_compute_to_secondary_uom",
        store=True,
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

    def _calculate_secondary_uom_qty(
        self, qty_on_hand, qty_forecast, uom_factor, uom_rounding
    ):
        """
        Calculate the quantity in the secondary unit.
        """
        secondary_uom_qty_on_hand = qty_on_hand / (uom_factor or 1.0)
        secondary_uom_qty_forecast = qty_forecast / (uom_factor or 1.0)
        return (
            float_round(secondary_uom_qty_on_hand, precision_rounding=uom_rounding),
            float_round(secondary_uom_qty_forecast, precision_rounding=uom_rounding),
        )

    def _compute_to_secondary_uom(self):
        """
        Compute the on hand and forecast quantities in the secondary unit.
        """
        for line in self:
            secondary_uom_qty_on_hand = 0.0
            secondary_uom_qty_forecast = 0.0
            if line.secondary_uom_id:
                secondary_uom_qty_on_hand, secondary_uom_qty_forecast = (
                    self._calculate_secondary_uom_qty(
                        line.qty_on_hand,
                        line.qty_forecast,
                        line.secondary_uom_id.factor,
                        line.product_uom.rounding,
                    )
                )
            line.write(
                {
                    "secondary_uom_qty_on_hand": secondary_uom_qty_on_hand,
                    "secondary_uom_qty_forecast": secondary_uom_qty_forecast,
                }
            )

    def _inverse_secondary_uom_qty(self):
        for line in self:
            if line.secondary_uom_id:
                line.qty_to_order = line.secondary_uom_qty * (
                    line.secondary_uom_id.factor or 1.0
                )
