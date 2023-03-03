# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestProductPackagingUom(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foot = cls.env.ref('uom.product_uom_foot')
        cls.meter = cls.env.ref('uom.product_uom_meter')
        cls.height = 1.35
        cls.packaging_length = 1.50
        cls.width = 2.88

    def test_foot_height_value_on_measure_is_float(self):
        self.product_package = self.env['product.packaging'].create({
            'name': 'Test product packaging',
            'height': self.height,
            'packaging_length': self.packaging_length,
            'width': self.width,
        })

        self.product_package.refresh()

        self.assertEqual(self.product_package.height, self.height)
        self.assertEqual(self.product_package.packaging_length, self.packaging_length)
        self.assertEqual(self.product_package.width, self.width)

    def test_product_packaging_uom(self):
        self.product_package_1_ft = self.env['product.packaging'].create({
            'name': 'Test product packaging - foot',
            'height': self.height,
            'height_uom_id': self.foot.id,
            'packaging_length': self.packaging_length,
            'length_uom_id': self.foot.id,
            'width': self.width,
            'width_uom_id': self.foot.id,
        })

        self.product_package_2_m = self.env['product.packaging'].create({
            'name': 'Test product packaging - meter',
            'height': self.height,
            'height_uom_id': self.meter.id,
            'packaging_length': self.packaging_length,
            'length_uom_id': self.meter.id,
            'width': self.width,
            'width_uom_id': self.meter.id,
        })

        self.product_package_1_ft.refresh()
        self.product_package_2_m.refresh()

        self.assertEqual(self.product_package_1_ft.height_uom_id, self.foot)
        self.assertEqual(self.product_package_1_ft.length_uom_id, self.foot)
        self.assertEqual(self.product_package_1_ft.width_uom_id, self.foot)
        self.assertEqual(self.product_package_2_m.height_uom_id, self.meter)
        self.assertEqual(self.product_package_2_m.length_uom_id, self.meter)
        self.assertEqual(self.product_package_2_m.width_uom_id, self.meter)
