# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    child_ids = fields.One2many("stock.move.line", "parent_id", "Child Move Lines")

    parent_id = fields.Many2one("stock.move.line", "Parent Move Line")

    def generate_component_moves(self):
        self.mapped("lot_id").pull_components()
