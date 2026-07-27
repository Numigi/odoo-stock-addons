# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import ValidationError

# Define plain string constants to allow proper lazy translation context resolution
WRONG_LOCATION_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved from the source location {location}. "
    "It is currently located in {serial_location}."
)

WRONG_PACKAGE_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved from the source package {package}. "
    "It is currently located in the package {serial_package}."
)

EXPECTED_PACKAGE_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved without a source package. "
    "It is currently located in the package {serial_package}."
)

UNEXPECTED_PACKAGE_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved from the source package {package}. "
    "It is not currently located in a package."
)

WRONG_OWNER_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved with the selected owner ({owner}). "
    "It is currently bound to the owner {serial_owner}."
)

EXPECTED_OWNER_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved without a source owner. "
    "It is currently bound to the owner {serial_owner}."
)

UNEXPECTED_OWNER_MESSAGE = (
    "The product {product} with the serial number {serial} "
    "can not be moved with the selected owner ({owner}). "
    "It is currently not bound to any owner."
)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def check_serial_number_constraints(self):
        self = self.sudo().with_context(lang=self.env.user.lang)
        self._check_serial_number_source_location()
        self._check_serial_number_source_package()
        self._check_serial_number_source_owner()

    def _requires_serial_check(self):
        dest_warehouse = self.location_dest_id.get_warehouse()
        is_bypassed = dest_warehouse.bypass_serial_single_quant
        has_quants = bool(self.lot_id.sudo().get_positive_quants())
        return not is_bypassed and has_quants

    def _check_serial_number_source_location(self):
        serial_locations = self.lot_id.get_current_location()
        if self.location_id not in serial_locations:
            self._raise_wrong_location_error(serial_locations)

    def _raise_wrong_location_error(self, serial_locations):
        location_names = ", ".join(serial_locations.mapped("display_name"))
        raise ValidationError(
            _(WRONG_LOCATION_MESSAGE).format(
                serial=self.lot_id.name,
                product=self.product_id.display_name,
                location=self.location_id.display_name,
                serial_location=location_names,
            )
        )

    def _check_serial_number_source_package(self):
        serial_package = self.lot_id.get_current_package()
        if self.package_id != serial_package:
            self._raise_package_error(serial_package)

    def _raise_package_error(self, serial_package):
        msg = self._get_package_error_message(serial_package)
        expected_name = serial_package.display_name if serial_package else ""
        current_name = self.package_id.name if self.package_id else ""

        raise ValidationError(
            _(msg).format(
                serial=self.lot_id.name,
                product=self.product_id.display_name,
                package=current_name,
                serial_package=expected_name,
            )
        )

    def _get_package_error_message(self, serial_package):
        if self.package_id and serial_package:
            return WRONG_PACKAGE_MESSAGE
        if self.package_id:
            return UNEXPECTED_PACKAGE_MESSAGE
        return EXPECTED_PACKAGE_MESSAGE

    def _check_serial_number_source_owner(self):
        serial_owner = self.lot_id.get_current_owner()
        if self.owner_id != serial_owner:
            self._raise_owner_error(serial_owner)

    def _raise_owner_error(self, serial_owner):
        msg = self._get_owner_error_message(serial_owner)
        expected_name = serial_owner.display_name if serial_owner else ""
        current_name = self.owner_id.name if self.owner_id else ""

        raise ValidationError(
            _(msg).format(
                serial=self.lot_id.name,
                product=self.product_id.display_name,
                owner=current_name,
                serial_owner=expected_name,
            )
        )

    def _get_owner_error_message(self, serial_owner):
        if self.owner_id and serial_owner:
            return WRONG_OWNER_MESSAGE
        if self.owner_id:
            return UNEXPECTED_OWNER_MESSAGE
        return EXPECTED_OWNER_MESSAGE
