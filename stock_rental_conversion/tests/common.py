# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockRentalConversionCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "My Warehouse", "code": "W1"}
        )

        cls.rental_product = cls.env["product.product"].create(
            {"name": "Rentalable Product", "type": "product", "tracking": "serial"}
        )

        cls.sales_product = cls.env["product.product"].create(
            {
                "name": "Salable Product",
                "type": "product",
                "tracking": "serial",
                "rental_product_id": cls.rental_product.id,
            }
        )

        cls.number = "123456"
        cls.sales_serial = cls.env["stock.production.lot"].create(
            {"product_id": cls.sales_product.id, "name": cls.number}
        )

        cls.source_location = cls.warehouse.lot_stock_id
        cls.destination_location = cls.warehouse.rental_location_id

        cls.quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.source_location.id,
                "lot_id": cls.sales_serial.id,
                "product_id": cls.sales_product.id,
                "quantity": 1,
            }
        )
