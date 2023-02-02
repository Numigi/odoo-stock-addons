# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class StockVirtualAdjustmentLine(models.Model):

    _name = "stock.virtual.adjustment.line"
    _description = "Virtual Inventory Adjustment Line"
    _order = "sequence"

    adjustment_id = fields.Many2one("stock.virtual.adjustment", required=True)
    sequence = fields.Integer()

    product_id = fields.Many2one("product.product", required=True)
    quantity = fields.Float(
        required=True,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    uom_id = fields.Many2one("uom.uom", "UoM", required=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.uom_id = self.product_id.uom_id

    def _confirm(self):
        self._check_can_be_confirmed()
        self._create_adjustment_move()
        self._create_reversal_move()

    def _check_can_be_confirmed(self):
        if self.product_id.cost_method == "fifo":
            raise ValidationError(
                _(
                    "The adjustment could not be confirmed. "
                    "The product {} is valued with the First In First Out method."
                ).format(self.product_id.display_name)
            )

    def _create_adjustment_move(self):
        vals = self._get_adjustment_move_vals()
        self._create_move(vals)

    def _create_reversal_move(self):
        vals = self._get_reversal_move_vals()
        self._create_move(vals)

    def _get_adjustment_move_vals(self):
        vals = self._get_common_move_vals()
        vals["name"] = self.adjustment_id.name
        vals["location_id"] = self.adjustment_id.location_id.id
        vals["location_dest_id"] = self.adjustment_id.location_dest_id.id
        vals["date"] = self.adjustment_id.adjustment_date
        self._reverse_locations_if_negative_quantity(vals)
        return vals

    def _get_reversal_move_vals(self):
        vals = self._get_common_move_vals()
        vals["name"] = "{} (Reversal)".format(self.adjustment_id.name)
        vals["location_id"] = self.adjustment_id.location_dest_id.id
        vals["location_dest_id"] = self.adjustment_id.location_id.id
        vals["date"] = self.adjustment_id.reversal_date
        self._reverse_locations_if_negative_quantity(vals)
        return vals

    def _get_common_move_vals(self):
        return {
            "company_id": self.adjustment_id.company_id.id,
            "product_id": self.product_id.id,
            "product_uom": self.uom_id.id,
            "product_uom_qty": abs(self.quantity),
            "state": "done",
            "origin": self.adjustment_id.name,
        }

    def _reverse_locations_if_negative_quantity(self, vals):
        if self.quantity < 0:
            location_id = vals["location_id"]
            location_dest_id = vals["location_dest_id"]
            vals["location_id"] = location_dest_id
            vals["location_dest_id"] = location_id

    def _create_move(self, vals):
        move = self.env["stock.move"].create(vals)
        self.adjustment_id.move_ids |= move
