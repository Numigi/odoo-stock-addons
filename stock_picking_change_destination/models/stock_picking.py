# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError

wizard_model = "stock.picking.change.destination"


class StockLocation(models.Model):
    _inherit = "stock.location"

    def is_in_the_same_warehouse_than(self, location):
        return self.get_warehouse() == location.get_warehouse()


class StockPicking(models.Model):
    _inherit = "stock.picking"

    location_dest_id = fields.Many2one(track_visibility="onchange")

    def button_open_location_destination_wizard(self):
        self.ensure_one()
        view = self.env.ref(
            "stock_picking_change_destination.stock_picking_change_destination_form"
        )
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
                    destination_moves=", ".join(destination_moves.mapped('display_name'))
                )
            )

        if self.location_dest_id.is_in_the_same_warehouse_than(stock_location):
            self.write({"location_dest_id": stock_location.id})
            self._set_stock_moves_location_destination()
        else:
            raise UserError(
                _(
                    # TODO: en attente du message final
                    "Not the same warehouse: {current_location} -> {new_location}"
                ).format(
                    current_location=self.location_dest_id.display_name,
                    new_location=stock_location.display_name,
                )
            )

    def _get_stock_moves_destination_moves(self):
        return self.move_lines.move_dest_ids

    def _set_stock_moves_location_destination(self):
        for move in self.move_lines:
            move.location_dest_id = self.location_dest_id.id


class StockPickingChangeDestLocation(models.TransientModel):
    _name = wizard_model

    location_dest_id = fields.Many2one(
        "stock.location", "Destination Location Zone", required=True
    )

    picking_id = fields.Many2one(
        "stock.picking", "Picking", required=True, ondelete="cascade"
    )

    @api.multi
    def set_location_destination(self):

        if self.location_dest_id and self.picking_id:
            picking = self.env["stock.picking"].browse(self.picking_id.id)

            if picking:
                picking.set_location_destination(self.location_dest_id)
