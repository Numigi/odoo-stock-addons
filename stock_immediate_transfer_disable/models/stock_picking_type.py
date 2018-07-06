# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    allow_imediate_transfer = fields.Boolean(
        'Allow Immediate Transfer')
