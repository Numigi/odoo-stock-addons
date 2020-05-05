# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    asset_ids = fields.One2many("account.asset", "serial_number_id", "Assets")
    asset_count = fields.Integer(compute="_compute_asset_count")

    def _compute_asset_count(self):
        for serial in self:
            serial.asset_count = len(serial.asset_ids)

    def open_linked_asset(self):
        if len(self.asset_ids) == 1:
            return self.asset_ids.get_formview_action()
        return self.env.ref("stock_serial_asset.linked_assets_action").read()[0]
