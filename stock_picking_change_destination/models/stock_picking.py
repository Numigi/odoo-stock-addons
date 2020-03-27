# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    location_dest_id = fields.Many2one(track_visibility="onchange")

    def button_open_location_destination_wizard(self):
        self.ensure_one()
        view = self.env.ref(
            "stock_picking_change_destination.stock_picking_change_destination_form"
        )
        wizard_model = "stock.picking.change.destination"
        wiz = self.env[wizard_model].create(
            {
                "location_dest_id": self.location_dest_id.id,
                "picking_id": self.id
            }
        )
        return {
            "name": _("Change Destination"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": wizard_model,
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }

    def set_location_destination(self, stock_location):
        destination_moves = self._get_stock_moves_destination_moves()
        if destination_moves:
            raise UserError(
                _(
                    "The picking destination could not be updated "
                    "as it is linked to the picking(s): {destination_moves}"
                ).format(
                    destination_moves=", ".join(destination_moves.mapped("display_name"))
                )
            )

        if self.location_dest_id.is_in_the_same_warehouse_than(stock_location):
            self.write({"location_dest_id": stock_location.id})
            self._set_stock_moves_location_destination()
        else:
            raise UserError(
                _(
                    "The picking destination could not be updated, "
                    "as the move between warehouses are not allowed."
                    " You should use a replenishment or a transit warehouse."
                )
            )

    def _get_stock_moves_destination_moves(self):
        return self.mapped("move_lines.move_dest_ids")

    def _set_stock_moves_location_destination(self):
        self.move_lines.write({"location_dest_id": self.location_dest_id.id})
        self._set_stock_move_lines_location_destination()

    def _set_stock_move_lines_location_destination(self):
        stock_move_lines = self.move_lines.mapped("move_line_ids")
        stock_move_lines.write({'location_dest_id': self.location_dest_id.id})
