# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.addons.stock_rental_conversion.tests.common import StockRentalConversionCase


class TestStockRentalConversionAccount(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conversion_account = cls.env["account.account"].create(
            {
                "name": "Rental Conversion Expense",
                "code": "511000",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )

        cls.wizard.conversion_account_id = cls.conversion_account
        cls.sales_product.property_valuation = "real_time"
        cls.sales_product.standard_price = 1000

        cls.rental_product.property_valuation = "real_time"
        cls.rental_product.standard_price = 1000

    def test_sales_move(self):
        self.wizard.validate()

        sales_move = self.wizard.sales_product_move_id
        debit = sales_move.account_move_ids.line_ids.filtered("debit")
        assert debit.account_id == self.conversion_account

        credit = sales_move.account_move_ids.line_ids.filtered("credit")
        assert credit.account_id != self.conversion_account

    def test_rental_move(self):
        self.wizard.validate()

        rental_move = self.wizard.rental_product_move_id

        debit = rental_move.account_move_ids.line_ids.filtered("debit")
        assert debit.account_id != self.conversion_account

        credit = rental_move.account_move_ids.line_ids.filtered("credit")
        assert credit.account_id == self.conversion_account
