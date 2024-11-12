# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingReservation(models.TransientModel):
    _name = "stock.picking.reservation"
    _description = "Stock Picking Reservation"

    def action_correct_reservation(self):
        server_action_id = self.sudo().env.ref(
            "stock.stock_quant_stock_move_line_desynchronization",
            raise_if_not_found=False,
        ).id
        return self.env["ir.actions.server"].sudo().browse(server_action_id).run()
