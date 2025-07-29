# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    move_location_dest_id = fields.Many2one(related="move_id.location_dest_id")
