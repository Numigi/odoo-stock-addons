# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, **kwargs):
        self._check_all_serial_number_constraints()
        return super()._action_done(**kwargs)

    def _check_all_serial_number_constraints(self):
        moves = self._get_serialized_moves()
        for move in moves:
            move._check_serial_number_constraints()

    def _get_serialized_moves(self):
        return self.filtered(lambda m: m.product_id.tracking == "serial")

    def _check_serial_number_constraints(self):
        lines = self._get_lines_to_check()
        for line in lines:
            line.check_serial_number_constraints()

    def _get_lines_to_check(self):
        return self.move_line_ids.filtered(lambda line: line._requires_serial_check())
