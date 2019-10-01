# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    enable_return_from_next_step = fields.Boolean()
