# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockImmediateTransfer(models.TransientModel):

    _inherit = 'stock.immediate.transfer'

    allow_imediate_transfer = fields.Boolean(
        related='pick_id.picking_type_id.allow_imediate_transfer',
        readonly=True)
