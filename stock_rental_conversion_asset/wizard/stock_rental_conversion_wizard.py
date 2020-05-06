# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
        vals = self._get_asset_account_move_values()
        move = self.env["account.move"].create(vals)
        move.post()

        if self.rental_lot_id:
            self.rental_lot_id.asset_ids = move.mapped("line_ids.asset_id")

    def _get_asset_account_move_values(self):
        debit_vals = self._get_asset_account_move_debit_values()
        credit_vals = self._get_asset_account_move_credit_values()
        return {
            "journal_id": self.asset_profile_id.journal_id.id,
            "ref": self._get_move_name(),
            "line_ids": [(0, 0, debit_vals), (0, 0, credit_vals)],
        }

    def _get_asset_account_move_debit_values(self):
        return {
            "name": self._get_asset_name(),
            "product_id": self.rental_product_id.id,
            "product_uom_id": self._get_uom().id,
            "quantity": 1,
            "account_id": self.asset_profile_id.account_asset_id.id,
            "debit": self._get_asset_purchase_value(),
            "asset_profile_id": self.asset_profile_id.id,
            "partner_id": False,
        }

    def _get_asset_account_move_credit_values(self):
        return {
            "name": self._get_asset_name(),
            "product_id": self.rental_product_id.id,
            "product_uom_id": self._get_uom().id,
            "quantity": 1,
            "account_id": self._get_asset_valuation_counterpart_account_id(),
            "credit": self._get_asset_purchase_value(),
        }

    def _get_asset_name(self):
        name = self.rental_product_id.display_name

        if self.rental_lot_id:
            name += " - " + self.rental_lot_id.name

        return name

    def _get_asset_purchase_value(self):
        value = -self.sales_product_move_id.value

        if not value:
            raise ValidationError(
                _(
                    "The asset could not be created for the rental product. "
                    "The selected salable product does have an inventory value."
                )
            )

        if value < 0:
            raise ValidationError(
                _(
                    "The asset could not be created for the rental product. "
                    "The selected salable product has a negative "
                    "inventory value."
                )
            )

        return value

    def _get_asset_valuation_counterpart_account_id(self):
        move = self.sales_product_move_id
        _, _, output_account_id, _ = move._get_accounting_data_for_valuation()
        return output_account_id
