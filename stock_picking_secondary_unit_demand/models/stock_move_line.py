# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    merged_qty_uom_info = fields.Char(
        string="Request Secondary Unit",
        readonly=True,
        related="move_id.merged_qty_uom_info",
    )
