# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestStockQuantPackageDimensionUomSpread(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foot = cls.env.ref("uom.product_uom_foot")
        cls.meter = cls.env.ref("uom.product_uom_meter")
        cls.height = 0.77
        cls.packaging_length = 9.80
        cls.width = 3.75

    def test_stock_quant_package_spreading_dimension_uom(self):
        self.stock_quant_package = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quand package - foot",
                "height": self.height,
                "height_uom_id": self.foot.id,
                "packaging_length": self.packaging_length,
                "length_uom_id": self.foot.id,
                "width": self.width,
                "width_uom_id": self.foot.id,
            }
        )

        self.product_packaging_type = self.env["product.packaging"].create(
            {
                "name": "Packaging type",
                "height": 8.5,
                "height_uom_id": self.meter.id,
                "packaging_length": 9.77,
                "length_uom_id": self.foot.id,
                "width": 22.01,
                "width_uom_id": self.foot.id,
            }
        )

        self.stock_quant_package.refresh()

        # onchange_value
        self.stock_quant_package.write(
            {"packaging_id": self.product_packaging_type.id})
        self.stock_quant_package._onchange_packaging_id()

        # dimensions
        self.assertEqual(
            self.stock_quant_package.height, self.product_packaging_type.height
        )
        self.assertEqual(
            self.stock_quant_package.packaging_length,
            self.product_packaging_type.packaging_length,
        )
        self.assertEqual(
            self.stock_quant_package.width, self.product_packaging_type.width
        )

        # uom
        self.assertEqual(
            self.stock_quant_package.height_uom_id,
            self.product_packaging_type.height_uom_id,
        )
        self.assertEqual(
            self.stock_quant_package.length_uom_id,
            self.product_packaging_type.length_uom_id,
        )
        self.assertEqual(
            self.stock_quant_package.width_uom_id,
            self.product_packaging_type.width_uom_id,
        )

