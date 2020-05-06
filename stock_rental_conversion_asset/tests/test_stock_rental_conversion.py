# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.addons.stock_rental_conversion.tests.common import StockRentalConversionCase
from odoo.exceptions import ValidationError


class StockRentalConversionCaseWithAssets(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.asset_account = cls._create_account("111001", "Asset", "asset")
        cls.depreciation_account = cls._create_account(
            "111002", "Depreciation", "asset"
        )
        cls.expense_account = cls._create_account(
            "511111", "Depreciation Expense", "expense"
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Depreciation Journal", "code": "DEP", "type": "general"}
        )

        cls.asset_profile = cls.env["account.asset.profile"].create(
            {
                "account_expense_depreciation_id": cls.expense_account.id,
                "account_asset_id": cls.asset_account.id,
                "account_depreciation_id": cls.depreciation_account.id,
                "journal_id": cls.journal.id,
                "name": "Hardware - 3 Years",
                "method_time": "year",
                "method_number": 3,
                "method_period": "year",
            }
        )

    @classmethod
    def _create_account(cls, code, name, internal_group):
        account_type = cls.env["account.account.type"].search(
            [("internal_group", "=", internal_group), ("type", "=", "other")], limit=1
        )
        return cls.env["account.account"].create(
            {"name": name, "code": code, "user_type_id": account_type.id}
        )


class TestWizardOnchange(StockRentalConversionCaseWithAssets):
    def test_automatically_set_asset_profile(self):
        self.sales_product.asset_profile_id = self.asset_profile
        vals_before = {"sales_product_id": self.sales_product.id}
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["sales_product_id"]
        )
        assert vals_after["asset_profile_id"] == self.asset_profile.id


class TestWizardValidation(StockRentalConversionCaseWithAssets):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cost = 1000
        cls.sales_product.standard_price = cls.cost
        cls.wizard = cls.env["stock.rental.conversion.wizard"].create(
            {
                "sales_product_id": cls.sales_product.id,
                "sales_lot_id": cls.sales_serial.id,
                "rental_product_id": cls.rental_product.id,
                "source_location_id": cls.source_location.id,
                "destination_location_id": cls.destination_location.id,
                "create_asset": True,
                "asset_profile_id": cls.asset_profile.id,
            }
        )

    def test_perpetual_inventory(self):
        self.sales_product.property_valuation = "real_time"
        self.wizard.validate()
        asset = self.wizard.rental_lot_id.asset_ids
        assert len(asset) == 1
        assert asset.profile_id == self.asset_profile
        assert len(asset.account_move_line_ids) == 1
        assert asset.purchase_value == self.cost

    def test_periodic_inventory(self):
        self.sales_product.property_valuation = "manual_periodic"
        self.wizard.validate()
        asset = self.wizard.rental_lot_id.asset_ids
        assert asset.purchase_value == self.cost

    def test_periodic_inventory_with_null_cost(self):
        self.sales_product.property_valuation = "manual_periodic"
        self.sales_product.standard_price = 0
        with pytest.raises(ValidationError):
            self.wizard.validate()

    def test_periodic_inventory_with_negative_cost(self):
        self.sales_product.property_valuation = "manual_periodic"
        self.sales_product.standard_price = -1
        with pytest.raises(ValidationError):
            self.wizard.validate()
