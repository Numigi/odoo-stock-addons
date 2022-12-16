# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from .common import StockInventoryCase


class TestStockInventoryValidation(StockInventoryCase):

    def test_if_product_in_category__error_not_raised(self):
        self.inventory.write({
            'category_id': self.category_1.id,
            'filter': 'category',
        })
        self.inventory.action_start()
        self.inventory.line_ids = self._new_inventory_line(self.product_a)
        self.inventory.action_validate()

    def test_if_product_not_in_category__raise_error(self):
        self.inventory.write({
            'category_id': self.category_1.id,
            'filter': 'category',
        })
        self.inventory.action_start()
        self.product_a.categ_id = self.category_2
        self.inventory.line_ids = self._new_inventory_line(self.product_a)
        with pytest.raises(ValidationError):
            self.inventory.action_validate()

    def test_if_single_product_selected__error_not_raised(self):
        self.inventory.write({
            'product_id': self.product_a.id,
            'filter': 'product',
        })
        self.inventory.action_start()
        self.inventory.line_ids = self._new_inventory_line(self.product_a)
        self.inventory.action_validate()

    def test_if_wrong_single_product_selected__raise_error(self):
        self.inventory.write({
            'product_id': self.product_a.id,
            'filter': 'product',
        })
        self.inventory.action_start()
        self.inventory.line_ids = self._new_inventory_line(self.product_b)
        with pytest.raises(ValidationError):
            self.inventory.action_validate()

    def test_if_lot_selected__error_not_raised(self):
        self.inventory.write({
            'lot_id': self.lot_b.id,
            'filter': 'lot',
        })
        self.inventory.action_start()
        self.inventory.line_ids = self._new_inventory_line(self.product_b, lot=self.lot_b)
        self.inventory.action_validate()

    def test_if_lot_not_selected__raise_error(self):
        self.inventory.write({
            'lot_id': self.lot_b.id,
            'filter': 'lot',
        })
        self.inventory.action_start()
        self.inventory.line_ids = self._new_inventory_line(self.product_b)
        with pytest.raises(ValidationError):
            self.inventory.action_validate()

    def test_if_wrong_lot_selected__raise_error(self):
        self.inventory.write({
            'lot_id': self.lot_b.id,
            'filter': 'lot',
        })
        self.inventory.action_start()
        wrong_lot = self.lot_b.copy({'name': 'Wrong Lot'})
        self.inventory.line_ids = self._new_inventory_line(self.product_b, lot=wrong_lot)
        with pytest.raises(ValidationError):
            self.inventory.action_validate()

    def _new_inventory_line(self, product, lot=None):
        return self.env['stock.inventory.line'].new({
            'prod_lot_id': lot.id if lot else None,
            'product_id': product.id,
            'location_id': self.inventory.location_id.id,
        })
