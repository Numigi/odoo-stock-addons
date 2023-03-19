# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    allow_imediate_transfer = fields.Boolean(
        compute="_compute_allow_imediate_transfer")

    @api.depends("pick_ids")
    def _compute_allow_imediate_transfer(self):
        for transfer in self:
            transfer.allow_imediate_transfer = all(
                transfer.mapped(
                    "pick_ids.picking_type_id.allow_imediate_transfer")
            )
