# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_done(self):
        res = super()._action_done()

        moves_with_components = self.filtered(lambda m: m._has_components())
        for move in moves_with_components:
            move.generate_component_moves()

        return res

    def _has_components(self):
        return bool(
            self.product_id.tracking == "serial"
            and self.mapped("move_line_ids.lot_id.component_line_ids")
        )

    def generate_component_moves(self):
        self.mapped("move_line_ids.lot_id").pull_components()
