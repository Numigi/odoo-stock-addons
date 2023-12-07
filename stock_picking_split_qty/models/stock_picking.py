# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class Picking(models.Model):
    _inherit = "stock.picking"

    def _create_new_move_lines(self, move_line_ids):
        move_lines_to_split = self.env["stock.move.line"]
        for ml in move_line_ids:
            if (
                float_compare(
                    ml.qty_done,
                    ml.product_uom_qty,
                    precision_rounding=ml.product_uom_id.rounding,
                )
                >= 0
            ):
                move_lines_to_split |= ml
            else:
                quantity_left_todo = float_round(
                    ml.product_uom_qty - ml.qty_done,
                    precision_rounding=ml.product_uom_id.rounding,
                    rounding_method="UP",
                )
                done_to_keep = ml.qty_done
                new_move_line = ml.copy(
                    default={"product_uom_qty": 0, "qty_done": ml.qty_done}
                )
                vals = {"product_uom_qty": quantity_left_todo, "qty_done": 0.0}
                ml.write(vals)
                new_move_line.write({"product_uom_qty": done_to_keep})
                move_lines_to_split |= new_move_line
        return True

    def _divide_stock_move_line(self, move_line_ids):
        for pick in self:
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if float_is_zero(
                move_line_ids[0].qty_done, precision_digits=precision_digits
            ):
                for line in move_line_ids:
                    line.qty_done = line.product_uom_qty

            self._create_new_move_lines(move_line_ids)

    def _prepare_move_lines(self, picking_move_lines):
        move_line_ids = picking_move_lines.filtered(
            lambda ml: float_compare(
                ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding
            )
            > 0
            and not ml.result_package_id
        )
        if not move_line_ids:
            move_line_ids = picking_move_lines.filtered(
                lambda ml: float_compare(
                    ml.product_uom_qty,
                    0.0,
                    precision_rounding=ml.product_uom_id.rounding,
                )
                > 0
                and float_compare(
                    ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding
                )
                == 0
            )
        return move_line_ids

    def action_divide_stock_move_line(self):
        self.ensure_one()
        if self.state in ("assigned") and self.picking_type_code == "outgoing":
            picking_move_lines = self.move_line_ids
            if (
                not self.picking_type_id.show_reserved
                and not self.immediate_transfer
                and not self.env.context.get("barcode_view")
            ):
                picking_move_lines = self.move_line_nosuggest_ids

            move_line_ids = self._prepare_move_lines(picking_move_lines)

            if move_line_ids:
                return self._divide_stock_move_line(move_line_ids)
            else:
                raise UserError(
                    _(
                        "Please add 'Done' quantities to the picking to split stock move."
                    )
                )
