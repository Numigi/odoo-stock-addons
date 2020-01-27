# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.addons.stock_inventory_line_domain.tests.common import StockInventoryCase


class TestStockInventoryValidation(StockInventoryCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.barcode_a = 'PROD_A'
        cls.product_a.barcode = cls.barcode_a
        cls.inventory.write({
            'category_id': cls.category_1.id,
            'filter': 'category',
        })

    def test_if_product_in_category__error_not_raised(self):
        self.inventory.on_barcode_scanned(self.barcode_a)

    def test_if_product_not_in_category__raise_error(self):
        self.product_a.categ_id = self.category_2
        with pytest.raises(ValidationError):
            self.inventory.on_barcode_scanned(self.barcode_a)
