# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_done(self):
        moves_with_serial_numbers = self.filtered(lambda m: m._has_serialized_product())
        for move in moves_with_serial_numbers:
            move._check_serial_number_constraints()
        return super()._action_done()

    def _has_serialized_product(self):
        return self.product_id.tracking == "serial"

    def _check_serial_number_constraints(self):
        lines_with_serial_number = self.move_line_ids.filtered(lambda l: l.lot_id)
        for line in lines_with_serial_number:
            line.check_serial_number_constraints()
