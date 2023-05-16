# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestStockQuantPackageDimension(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foot = cls.env.ref("uom.product_uom_foot")
        cls.meter = cls.env.ref("uom.product_uom_meter")
        cls.inch = cls.env.ref("uom.product_uom_inch")
        cls.cm = cls.env.ref("uom.product_uom_cm")
        cls.height = 0.38
        cls.packaging_length = 0.80
        cls.width = 3.77

    def test_stock_quant_dimension_with_decimal(self):
        self.stock_quant_package = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quant package",
                "height": self.height,
                "packaging_length": self.packaging_length,
                "width": self.width,
            }
        )

        self.stock_quant_package.refresh()

        self.assertEqual(self.stock_quant_package.height, self.height)
        self.assertEqual(
            self.stock_quant_package.packaging_length, self.packaging_length
        )
        self.assertEqual(self.stock_quant_package.width, self.width)

    def test_stock_quant_package_dimension_uom(self):
        self.stock_quant_package_ft = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quant package - foot",
                "height": self.height,
                "height_uom_id": self.foot.id,
                "packaging_length": self.packaging_length,
                "length_uom_id": self.foot.id,
                "width": self.width,
                "width_uom_id": self.foot.id,
            }
        )

        self.stock_quant_package_m = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quant package - meter",
                "height": self.height,
                "height_uom_id": self.meter.id,
                "packaging_length": self.packaging_length,
                "length_uom_id": self.meter.id,
                "width": self.width,
                "width_uom_id": self.meter.id,
            }
        )

        self.stock_quant_package_inch = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quant package - inch",
                "height": self.height,
                "height_uom_id": self.inch.id,
                "packaging_length": self.packaging_length,
                "length_uom_id": self.inch.id,
                "width": self.width,
                "width_uom_id": self.inch.id,
            }
        )

        self.stock_quant_package_cm = self.env["stock.quant.package"].create(
            {
                "name": "Test stock quant package - cm",
                "height": self.height,
                "height_uom_id": self.cm.id,
                "packaging_length": self.packaging_length,
                "length_uom_id": self.cm.id,
                "width": self.width,
                "width_uom_id": self.cm.id,
            }
        )

        self.stock_quant_package_ft.refresh()
        self.stock_quant_package_m.refresh()

        self.assertEqual(self.stock_quant_package_ft.height_uom_id, self.foot)
        self.assertEqual(self.stock_quant_package_ft.length_uom_id, self.foot)
        self.assertEqual(self.stock_quant_package_ft.width_uom_id, self.foot)
        self.assertEqual(self.stock_quant_package_m.height_uom_id, self.meter)
        self.assertEqual(self.stock_quant_package_m.length_uom_id, self.meter)
        self.assertEqual(self.stock_quant_package_m.width_uom_id, self.meter)
        self.assertEqual(
            self.stock_quant_package_inch.height_uom_id, self.inch)
        self.assertEqual(
            self.stock_quant_package_inch.length_uom_id, self.inch)
        self.assertEqual(
            self.stock_quant_package_inch.width_uom_id, self.inch)
        self.assertEqual(self.stock_quant_package_cm.height_uom_id, self.cm)
        self.assertEqual(self.stock_quant_package_cm.length_uom_id, self.cm)
        self.assertEqual(self.stock_quant_package_cm.width_uom_id, self.cm)
