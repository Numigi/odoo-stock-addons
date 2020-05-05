# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import api, fields, models


class StockRentalConversionWizard(models.TransientModel):

    _inherit = "stock.rental.conversion.wizard"

    asset_profile_id = fields.Many2one("account.asset.profile")

    create_asset = fields.Boolean()

    @api.onchange("sales_product_id")
    def _propagate_asset_profile_from_sale_product(self):
        self.asset_profile_id = self.sales_product_id.asset_profile_id
        self.create_asset = bool(self.asset_profile_id)

    def validate(self):
        super().validate()

        if self.create_asset:
            self._create_asset()

    def _create_asset(self):
        vals = self._get_asset_values()
        self.env["account.asset"].create(vals)

    def _get_asset_values(self):
        vals = self.env["account.asset"].play_onchanges(
            {"profile_id": self.asset_profile_id.id}, ["profile_id"]
        )
        vals["name"] = self._get_asset_name()
        vals["serial_number_id"] = self.rental_lot_id.id
        vals["date_start"] = datetime.now()
        vals["purchase_value"] = self._get_asset_purchase_value()
        return vals

    def _get_asset_name(self):
        name = self.rental_product_id.display_name

        if self.rental_lot_id:
            name += " - " + self.rental_lot_id.name

        return name

    def _get_asset_purchase_value(self):
        return self.rental_product_id.standard_price
