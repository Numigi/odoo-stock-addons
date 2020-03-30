# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from .common import StockMoveCase


class TestStockMoves(StockMoveCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quant_1 = cls.make_quant(cls.location_1, cls.serial_1)

    def test_non_serialized_product(self):
        product = self.env["product.product"].create(
            {"name": "Product Tracked By Lot", "type": "product", "tracking": "lot"}
        )
        lot = self.make_serial_number("LOT-1", product)
        self.make_quant(self.location_1, lot)
        self.move_serial_number(lot, self.location_2, self.location_3)

    def test_correct_source_location(self):
        self.move_serial_number(self.serial_1, self.location_1, self.location_3)
        assert self.serial_1.get_current_location() == self.location_3

    def test_wrong_source_location(self):
        with pytest.raises(ValidationError):
            self.move_serial_number(self.serial_1, self.location_2, self.location_3)

    def test_correct_source_package(self):
        self.quant_1.package_id = self.package_1
        self.move_serial_number(
            self.serial_1,
            self.location_1,
            self.location_2,
            package_src=self.package_1,
            package_dest=self.package_2,
        )
        assert self.serial_1.get_current_package() == self.package_2

    def test_wrong_source_package(self):
        self.quant_1.package_id = self.package_1
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1,
                self.location_1,
                self.location_2,
                package_src=self.package_2,
                package_dest=self.package_2,
            )

    def test_correct_source_owner(self):
        self.quant_1.owner_id = self.owner_1
        self.move_serial_number(
            self.serial_1, self.location_1, self.location_2, owner_src=self.owner_1
        )
        assert self.serial_1.get_current_owner() == self.owner_1

    def test_wrong_source_owner(self):
        self.quant_1.owner_id = self.owner_1
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1, self.location_1, self.location_2, owner_src=self.owner_2
            )
