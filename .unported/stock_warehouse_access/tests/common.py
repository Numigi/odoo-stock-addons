# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class StockAccessCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Warehouse 1',
            'code': 'WH1-TEST',
        })

        cls.warehouse_2 = cls.env['stock.warehouse'].create({
            'name': 'Warehouse 2',
            'code': 'WH2-TEST',
        })

        cls.user = cls.env['res.users'].create({
            'name': 'Stock User',
            'email': 'stock.user@example.com',
            'login': 'stock.user@example.com',
            'all_warehouses': False,
            'warehouse_ids': [(4, cls.warehouse_1.id)],
            'groups_id': [
                (4, cls.env.ref('stock.group_stock_manager').id),
            ]
        })

        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')

        cls.location_1 = cls.env['stock.location'].create({
            'name': 'Location 1',
            'location_id': cls.warehouse_1.lot_stock_id.id,
        })

        cls.location_2 = cls.env['stock.location'].create({
            'name': 'Location 2',
            'location_id': cls.warehouse_2.lot_stock_id.id,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'My Product',
            'type': 'product',
        })

        stock_locations = (
            cls.warehouse_1.lot_stock_id |
            cls.warehouse_2.lot_stock_id |
            cls.location_1 |
            cls.location_2
        )

        for location in stock_locations:
            cls.env['stock.quant'].create({
                'product_id': cls.product.id,
                'quantity': 100,
                'location_id': location.id,
            })
