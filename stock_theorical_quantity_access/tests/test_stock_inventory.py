# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from odoo.tests.common import SavepointCase


@ddt
class TestStockInventory(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create and validate an initial inventory
        # to make sure at least one products has theoretical quantities.
        initial_inventory = cls.env['stock.inventory'].create({
            'name': 'Initial Inventory',
            'filter': 'none',
            'exhausted': True,
        })
        product = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
        })
        initial_inventory.action_start()
        line = next(l for l in initial_inventory.line_ids if l.product_id == product)
        line.product_qty = 1
        initial_inventory.action_validate()

        cls.inventory = cls.env['stock.inventory'].create({
            'name': 'My Inventory',
            'exhausted': False,
        })

    @data(
        ('none', True),
        ('category', True),
        ('product', False),
        ('partial', False),
    )
    @unpack
    def test_onchange_filter__exausted_updated(self, filter_type, exausted):
        with self.env.do_in_onchange():
            self.inventory.filter = filter_type
            self.inventory._onchange_filter_set_exhausted()

    def test_theoritical_quantity_is_zero(self):
        self.inventory.filter = 'none'
        self.inventory.action_start()
        assert sum(self.inventory.mapped('line_ids.product_qty')) == 0

    def test_onchange_product__quantity_set_to_zero(self):
        self.inventory.filter = 'none'
        self.inventory.action_start()

        for line in self.inventory.line_ids:
            line._onchange_quantity_context()

        assert sum(self.inventory.mapped('line_ids.product_qty')) == 0
