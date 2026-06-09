# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves_with_serial_numbers = self.filtered(lambda m: m._has_serialized_product())
        for move in moves_with_serial_numbers:
            move._check_serial_number_constraints()
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _has_serialized_product(self):
        return self.product_id.tracking == "serial"

    def _check_serial_number_constraints(self):
        lines_to_check = self._get_lines_to_check()
        for line in lines_to_check:
            line.check_serial_number_constraints()

    def _get_lines_to_check(self):
        return self.move_line_ids.filtered(lambda line: line._requires_serial_check())
