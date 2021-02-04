# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import StockRentalConversionCase


class TestWizardOnchange(StockRentalConversionCase):
    def test_automatically_set_rental_product(self):
        vals_before = {"sales_product_id": self.sales_product.id}
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["sales_product_id"]
        )
        assert vals_after["rental_product_id"] == self.rental_product.id

    def test_source_default_values(self):
        vals_before = {
            "sales_product_id": self.sales_product.id,
            "sales_lot_id": self.sales_serial.id,
        }
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["sales_lot_id"]
        )
        assert vals_after["source_location_id"] == self.source_location.id
        assert vals_after["destination_location_id"] == self.destination_location.id


class TestWizardValidation(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard.validate()
        cls.rental_serial = cls.wizard.rental_lot_id

    def test_rental_serial_number(self):
        assert self.rental_serial.name == self.number
        assert self.rental_serial.product_id == self.rental_product
        assert self.rental_serial.sales_lot_id == self.sales_serial
        assert self.rental_serial.get_current_location() == self.destination_location

    def test_sales_serial_number(self):
        assert self.sales_serial.get_current_location().usage == "production"


class TestWizardWithNonSerializedProduct(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sales_product.tracking = "none"
        cls.rental_product.tracking = "none"
        cls.quant.lot_id = False
        cls.wizard.rental_lot_id = False
        cls.wizard.validate()

    def test_sales_product_moved_to_production(self):
        new_quant = self.env["stock.quant"].search(
            [("product_id", "=", self.sales_product.id), ("quantity", "!=", 0)]
        )
        assert new_quant.quantity == 1
        assert new_quant.location_id.usage == "production"

    def test_rental_product_moved_to_destination(self):
        new_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.rental_product.id),
                ("quantity", "!=", 0),
                ("location_id.usage", "!=", "production"),
            ]
        )
        assert new_quant.quantity == 1
        assert new_quant.location_id == self.destination_location
