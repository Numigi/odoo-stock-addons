# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import ValidationError


WRONG_LOCATION_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved from the source location {location}. "
    "It is currently located in {serial_location}."
)

WRONG_PACKAGE_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved from the source package {package}. "
    "It is currently located in the package {serial_package}."
)

EXPECTED_PACKAGE_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved without a source package. "
    "It is currently located in the package {serial_package}."
)

UNEXPECTED_PACKAGE_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved from the source package {package}. "
    "It is not currently located in a package."
)

WRONG_OWNER_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved with the selected owner ({owner}). "
    "It is currently bound to the owner {serial_owner}."
)

EXPECTED_OWNER_MESSAGE = _(
    "The product {product} with the serial number {serial} "
    "can not be moved without a source owner. "
    "It is currently bound to the owner {serial_owner}."
)

UNEXPECTED_OWNER_MESSAGE = _(
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

    def _check_serial_number_source_location(self):
        serial_location = self.lot_id.get_current_location()
        if serial_location != self.location_id:
            raise ValidationError(
                _(WRONG_LOCATION_MESSAGE).format(
                    serial=self.lot_id.name,
                    product=self.product_id.display_name,
                    location=self.location_id.display_name,
                    serial_location=serial_location.display_name,
                )
            )

    def _check_serial_number_source_package(self):
        serial_package = self.lot_id.get_current_package()
        if self.package_id != serial_package:
            if self.package_id and serial_package:
                message = WRONG_PACKAGE_MESSAGE
            elif self.package_id:
                message = UNEXPECTED_PACKAGE_MESSAGE
            else:
                message = EXPECTED_PACKAGE_MESSAGE

            raise ValidationError(
                _(message).format(
                    serial=self.lot_id.name,
                    product=self.product_id.display_name,
                    package=self.package_id.name,
                    serial_package=serial_package.display_name,
                )
            )

    def _check_serial_number_source_owner(self):
        serial_owner = self.lot_id.get_current_owner()
        if self.owner_id != serial_owner:
            if self.package_id and serial_owner:
                message = WRONG_OWNER_MESSAGE
            elif self.package_id:
                message = UNEXPECTED_OWNER_MESSAGE
            else:
                message = EXPECTED_OWNER_MESSAGE

            raise ValidationError(
                _(message).format(
                    serial=self.lot_id.name,
                    product=self.product_id.display_name,
                    owner=self.owner_id.name,
                    serial_owner=serial_owner.display_name,
                )
            )
