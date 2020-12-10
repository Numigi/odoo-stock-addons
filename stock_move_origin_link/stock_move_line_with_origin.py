# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLineWithOrigin(models.Model):

    _inherit = "stock.move.line"

    origin = fields.Char(related="move_id.origin", readonly=True)
