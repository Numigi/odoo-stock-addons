# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.addons.stock_serial_single_quant.tests.common import StockMoveCase


class TestShadowMoves(StockMoveCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quant_1 = cls.make_quant(cls.location_1, cls.serial_1)
        cls.quant_2 = cls.make_quant(cls.location_1, cls.serial_2)
        cls.quant_3 = cls.make_quant(cls.location_1, cls.serial_3)
        cls.serial_1.add_component(cls.serial_2)

    def test_child_component(self):
        self.move_serial_number(self.serial_1, self.location_1, self.location_2)
        for serial in self.serial_1 | self.serial_2:
            assert serial.get_current_location() == self.location_2

    def test_grand_child_component(self):
        self.serial_2.add_component(self.serial_3)
        self.move_serial_number(self.serial_1, self.location_1, self.location_2)
        for serial in self.serial_1 | self.serial_2 | self.serial_3:
            assert serial.get_current_location() == self.location_2

    def test_two_child_components(self):
        self.serial_1.add_component(self.serial_3)
        self.move_serial_number(self.serial_1, self.location_1, self.location_2)
        for serial in self.serial_1 | self.serial_2 | self.serial_3:
            assert serial.get_current_location() == self.location_2

    def test_source_package(self):
        self.quant_1.package_id = self.package_1
        self.quant_2.package_id = self.package_1
        self.move_serial_number(
            self.serial_1, self.location_1, self.location_2, package_src=self.package_1
        )
        for serial in self.serial_1 | self.serial_2:
            assert serial.get_current_location() == self.location_2
            assert not serial.get_current_package()

    def test_destination_package(self):
        self.move_serial_number(
            self.serial_1, self.location_1, self.location_2, package_dest=self.package_1
        )
        for serial in self.serial_1 | self.serial_2:
            assert serial.get_current_location() == self.location_2
            assert serial.get_current_package() == self.package_1

    def test_source_and_destination_package(self):
        self.quant_1.package_id = self.package_1
        self.quant_2.package_id = self.package_1
        self.move_serial_number(
            self.serial_1,
            self.location_1,
            self.location_2,
            package_src=self.package_1,
            package_dest=self.package_2,
        )
        for serial in self.serial_1 | self.serial_2:
            assert serial.get_current_location() == self.location_2
            assert serial.get_current_package() == self.package_2

    def test_wrong_source_package(self):
        self.quant_1.package_id = self.package_1
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1,
                self.location_1,
                self.location_2,
                package_src=self.package_2,
            )
