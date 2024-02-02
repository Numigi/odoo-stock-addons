# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    valuation_adjustment_line_ids = fields.One2many(
        "stock.valuation.adjustment.lines", "move_id"
    )
    value = fields.Float(string="Value", compute="_compute_total_value")

    @api.depends("stock_valuation_layer_ids")
    def _compute_total_value(self):
        for stock_move in self:
            stock_move.value = sum(
                [(svl.value) for svl in stock_move.stock_valuation_layer_ids]
            )
