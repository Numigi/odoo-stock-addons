# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.addons.stock_serial_single_quant.tests.common import StockMoveCase


class TestStockProductionLot(StockMoveCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quant_1 = cls.make_quant(cls.location_1, cls.serial_1)

    def test_add_serial__same_location(self):
        self.make_quant(self.location_1, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.parent_component_id == self.serial_1

    def test_add_serial__child_location(self):
        old_quant = self.make_quant(self.location_1a, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.get_current_location() == self.location_1
        assert old_quant.quantity == 0

    def test_add_serial__grand_child_location(self):
        old_quant = self.make_quant(self.location_1aa, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.get_current_location() == self.location_1
        assert old_quant.quantity == 0

    def test_add_serial__different_location(self):
        self.make_quant(self.location_2, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_package(self):
        self.make_quant(self.location_1, self.serial_2, package=self.package_1)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_same_package(self):
        self.quant_1.package_id = self.package_1
        self.make_quant(self.location_1, self.serial_2, package=self.package_1)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_2.get_non_zero_quants().package_id == self.package_1

    def test_add_serial__quant_with_owner(self):
        self.make_quant(self.location_1, self.serial_2, owner=self.owner_1)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_same_owner(self):
        self.quant_1.owner_id = self.owner_1
        self.make_quant(self.location_1, self.serial_2, owner=self.owner_1)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_2.get_non_zero_quants().owner_id == self.owner_1

    def test_add_serial__quant_with_reserved_quantity(self):
        quant = self.make_quant(self.location_1, self.serial_2)
        quant.reserved_quantity = 1
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_parent_has_2_quants__raise_error(self):
        self.make_quant(self.location_1, self.serial_1)
        self.make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_component_has_2_quants__raise_error(self):
        self.make_quant(self.location_1, self.serial_2)
        self.make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_parent_has_no_quant__raise_error(self):
        self.make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_3.add_component(self.serial_2)

    def test_if_component_has_no_quant__raise_error(self):
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_component_can_not_have_2_parents(self):
        self.make_quant(self.location_1, self.serial_2)
        self.make_quant(self.location_1, self.serial_3)
        self.serial_1.add_component(self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_3.add_component(self.serial_2)

    def test_parent_can_not_have_2_times_same_component(self):
        self.make_quant(self.location_1, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)
