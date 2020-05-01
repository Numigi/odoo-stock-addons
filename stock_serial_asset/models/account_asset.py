# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountAsset(models.Model):

    _inherit = "account.asset"

    serial_number_ids = fields.Many2many(
        "stock.production.lot",
        "stock_production_lot_asset_rel",
        "lot_id",
        "asset_id",
        "Serial Numbers",
    )
    serial_number_count = fields.Integer(compute="_compute_serial_number_count")

    def _compute_serial_number_count(self):
        for asset in self:
            asset.serial_number_count = len(asset.serial_number_ids)

    def open_linked_serial_numbers(self):
        if len(self.asset_ids) == 1:
            return self.asset_ids.get_formview_action()

        action = self.env.ref("stock_serial_asset.linked_serial_numbers_action").read()[
            0
        ]
        action["domain"] = [("asset_ids", "=", self.id)]
        return action
