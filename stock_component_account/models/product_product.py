# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class Product(models.Model):

    _inherit = "product.product"

    def _compute_average_price(self, qty_done, quantity, moves):
        is_serialized_move = bool(moves.mapped("move_line_ids.lot_id.is_serial"))
        if is_serialized_move:
            return self._compute_average_price_including_components(
                qty_done, quantity, moves
            )
        else:
            return super()._compute_average_price(qty_done, quantity, moves)

    def _compute_average_price_including_components(self, qty_done, quantity, moves):
        done_moves = moves.filtered(lambda m: m.state == "done")
        done_lines = done_moves.mapped("move_line_ids").sorted(
            key=lambda l: (l.date, l.id)
        )

        start_index = int(qty_done)
        end_index = int(qty_done + quantity)
        lines_to_include = done_lines[start_index:end_index]

        total = sum(abs(l.get_total_unit_price()) for l in lines_to_include)
        return total / len(lines_to_include) if lines_to_include else 0
