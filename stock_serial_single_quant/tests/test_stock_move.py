# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
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
        product = self._make_non_serialized_product()
        lot = self.make_serial_number("LOT-1", product)
        self.make_quant(self.location_1, lot)
        self.move_serial_number(lot, self.location_2, self.location_3)

    def test_is_serial(self):
        assert self.serial_1.is_serial

    def test_is_not_serial(self):
        product = self._make_non_serialized_product()
        lot = self.make_serial_number("LOT-1", product)
        assert not lot.is_serial

    def _make_non_serialized_product(self):
        return self.env["product.product"].create(
            {"name": "Product Tracked By Lot", "type": "product", "tracking": "lot"}
        )

    def test_serial_number_with_no_quant(self):
        self.move_serial_number(self.serial_2, self.location_1, self.location_2)
        assert self.serial_2.get_current_location() == self.location_2

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

    def test_unexpected_source_package(self):
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1,
                self.location_1,
                self.location_2,
                package_src=self.package_1,
                package_dest=self.package_2,
            )

    def test_expected_source_package(self):
        self.quant_1.package_id = self.package_1
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1,
                self.location_1,
                self.location_2,
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

    def test_unexpected_source_owner(self):
        with pytest.raises(ValidationError):
            self.move_serial_number(
                self.serial_1, self.location_1, self.location_2, owner_src=self.owner_1
            )

    def test_expected_source_owner(self):
        self.quant_1.owner_id = self.owner_1
        with pytest.raises(ValidationError):
            self.move_serial_number(self.serial_1, self.location_1, self.location_2)

    def test_bypass_serial_single_quant_enabled(self):
        # Enable the bypass on the destination warehouse
        self.warehouse_3.bypass_serial_single_quant = True
        # Move the serial number from an invalid location (location_2)
        # to the bypassed warehouse (location_3)
        # It should NOT raise a ValidationError because the check is bypassed
        move = self.move_serial_number(self.serial_1, self.location_2, self.location_3)

        assert move.state == "done"
        expected_locations = self.location_1 | self.location_3
        assert self.serial_1.get_current_location() == expected_locations

    def test_multi_quant_raises_validation_error_not_singleton(self):
        # Create a second quant for the same serial in a different location (incoherence)
        self.make_quant(self.location_2, self.serial_1)

        # Now serial_1 is physically in both location_1 and location_2.
        # Moving it from a completely different location (location_1a) should raise a
        # ValidationError and NOT a ValueError (Expected Singleton)
        with pytest.raises(ValidationError) as excinfo:
            self.move_serial_number(self.serial_1, self.location_1a, self.location_3)

        # Verify that both locations are correctly joined and displayed in the error message
        error_message = str(excinfo.value)
        assert self.location_1.display_name in error_message
        assert self.location_2.display_name in error_message

    def test_bypass_disabled_still_raises_error(self):
        # Ensure that by default (bypass = False), the error is still raised
        self.warehouse_3.bypass_serial_single_quant = False

        with pytest.raises(ValidationError):
            self.move_serial_number(self.serial_1, self.location_2, self.location_3)
