# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    merged_qty_uom_info = fields.Char(
        string="Request Secondary Unit",
        readonly=True,
        store=True
    )
