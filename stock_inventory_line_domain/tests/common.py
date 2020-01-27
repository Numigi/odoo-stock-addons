# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockInventoryCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_1 = cls.env['product.category'].create({'name': 'Category 1'})
        cls.category_2 = cls.env['product.category'].create({'name': 'Category 2'})
        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'categ_id': cls.category_1.id,
            'type': 'product',
        })
        cls.product_b = cls.env['product.product'].create({
            'name': 'Product B',
            'categ_id': cls.category_1.id,
            'tracking': 'lot',
            'type': 'product',
        })
        cls.lot_b = cls.env['stock.production.lot'].create({
            'name': '12345',
            'product_id': cls.product_b.id,
        })

        cls.inventory = cls.env['stock.inventory'].create({
            'name': 'New Inventory',
        })
