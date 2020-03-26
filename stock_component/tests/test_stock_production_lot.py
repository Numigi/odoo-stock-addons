# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestStockProductionLot(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse_1 = cls._make_warehouse("W1")
        cls.warehouse_2 = cls._make_warehouse("W2")

        cls.product_1 = cls._make_product("P1")
        cls.product_2 = cls._make_product("P2")
        cls.product_3 = cls._make_product("P3")

        cls.serial_1 = cls._make_serial_number("S1", cls.product_1)
        cls.serial_2 = cls._make_serial_number("S2", cls.product_2)
        cls.serial_3 = cls._make_serial_number("S3", cls.product_2)

        cls.location_1 = cls.warehouse_1.lot_stock_id
        cls.location_2 = cls.warehouse_2.lot_stock_id

        cls.location_1a = cls._make_location(cls.location_1, "A")
        cls.location_1aa = cls._make_location(cls.location_1a, "AA")

        cls.quant_1 = cls._make_quant(cls.location_1, cls.serial_1)

        cls.package_1 = cls._make_package("P1", cls.location_1)

        cls.owner_1 = cls.env.user.partner_id

    @classmethod
    def _make_product(cls, name):
        return cls.env["product.product"].create({"name": name, "type": "product"})

    @classmethod
    def _make_serial_number(cls, name, product):
        return cls.env["stock.production.lot"].create(
            {"name": name, "product_id": product.id}
        )

    @classmethod
    def _make_location(cls, parent, name):
        return cls.env["stock.location"].create(
            {"name": name, "location_id": parent.id, "usage": "internal"}
        )

    @classmethod
    def _make_quant(cls, location, serial, package=None, owner=None):
        return cls.env["stock.quant"].create(
            {
                "product_id": serial.product_id.id,
                "lot_id": serial.id,
                "location_id": location.id,
                "quantity": 1,
                "package_id": package.id if package else None,
                "owner_id": owner.id if owner else None,
            }
        )

    @classmethod
    def _make_package(cls, name, location):
        return cls.env["stock.quant.package"].create(
            {
                "name": name,
                "location_id": location.id,
            }
        )

    @classmethod
    def _make_warehouse(cls, name):
        return cls.env["stock.warehouse"].create(
            {
                "name": name,
                "code": name,
            }
        )

    def test_add_serial__same_location(self):
        self._make_quant(self.location_1, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.parent_component_id == self.serial_1

    def test_add_serial__child_location(self):
        old_quant = self._make_quant(self.location_1a, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.get_current_location() == self.location_1
        assert old_quant.quantity == 0

    def test_add_serial__grand_child_location(self):
        old_quant = self._make_quant(self.location_1aa, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_1.component_ids == self.serial_2
        assert self.serial_2.get_current_location() == self.location_1
        assert old_quant.quantity == 0

    def test_add_serial__different_location(self):
        self._make_quant(self.location_2, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_package(self):
        self._make_quant(self.location_1, self.serial_2, package=self.package_1)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_same_package(self):
        self.quant_1.package_id = self.package_1
        self._make_quant(self.location_1, self.serial_2, package=self.package_1)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_2.get_non_zero_quants().package_id == self.package_1

    def test_add_serial__quant_with_owner(self):
        self._make_quant(self.location_1, self.serial_2, owner=self.owner_1)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_add_serial__quant_in_same_owner(self):
        self.quant_1.owner_id = self.owner_1
        self._make_quant(self.location_1, self.serial_2, owner=self.owner_1)
        self.serial_1.add_component(self.serial_2)
        assert self.serial_2.get_non_zero_quants().owner_id == self.owner_1

    def test_add_serial__quant_with_reserved_quantity(self):
        quant = self._make_quant(self.location_1, self.serial_2)
        quant.reserved_quantity = 1
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_parent_has_2_quants__raise_error(self):
        self._make_quant(self.location_1, self.serial_1)
        self._make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_component_has_2_quants__raise_error(self):
        self._make_quant(self.location_1, self.serial_2)
        self._make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_if_parent_has_no_quant__raise_error(self):
        self._make_quant(self.location_1, self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_3.add_component(self.serial_2)

    def test_if_component_has_no_quant__raise_error(self):
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)

    def test_component_can_not_have_2_parents(self):
        self._make_quant(self.location_1, self.serial_2)
        self._make_quant(self.location_1, self.serial_3)
        self.serial_1.add_component(self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_3.add_component(self.serial_2)

    def test_parent_can_not_have_2_times_same_component(self):
        self._make_quant(self.location_1, self.serial_2)
        self.serial_1.add_component(self.serial_2)
        with pytest.raises(ValidationError):
            self.serial_1.add_component(self.serial_2)
