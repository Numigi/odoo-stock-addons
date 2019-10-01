# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockReturnCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Warehouse 1',
            'code': 'WH1-TEST',
        })
        cls.warehouse.delivery_steps = 'pick_ship'

        cls.ship_type = cls.warehouse.out_type_id
        cls.ship_type.enable_return_from_next_step = True

        cls.stock_user = cls.env['res.users'].create({
            'name': 'Stock User',
            'login': 'test_stock_user',
            'email': 'test_stock_user@test.com',
            'groups_id': [(4, cls.env.ref('stock.group_stock_user').id)]
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'My Product',
            'type': 'product',
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'My Product B',
            'type': 'product',
        })

        for product in (cls.product_a, cls.product_b):
            cls.env['stock.quant'].create({
                'location_id': cls.warehouse.lot_stock_id.id,
                'product_id': product.id,
                'quantity': 100,
            })

        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'warehouse_id': cls.warehouse.id,
            'order_line': [
                (0, 0, {
                    'product_id': cls.product_a.id,
                    'name': cls.product_a.display_name,
                    'product_uom': cls.env.ref('product.product_uom_unit').id,
                    'product_uom_qty': 10,
                }),
                (0, 0, {
                    'product_id': cls.product_b.id,
                    'name': cls.product_b.display_name,
                    'product_uom': cls.env.ref('product.product_uom_unit').id,
                    'product_uom_qty': 10,
                }),
            ]
        })
        cls.sale_order.action_confirm()
        cls.delivery = cls.sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id == cls.ship_type
        )
        cls.pick = cls.sale_order.picking_ids - cls.delivery

    @staticmethod
    def select_quantities(picking, product, quantity):
        move = picking.move_lines.filtered(lambda m: m.product_id == product)
        move._action_assign()
        move.move_line_ids.qty_done = quantity

    def return_products(self):
        wizard_action = self.delivery.button_validate()
        wizard = self.env['stock.backorder.confirmation'].browse(wizard_action['res_id'])
        return_picking_id = wizard.return_products()['res_id']
        return self.env['stock.picking'].browse(return_picking_id)


class TestStockReturn(StockReturnCase):
    """Test the case where all products are processed on the first step."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.select_quantities(cls.pick, cls.product_a, 10)
        cls.select_quantities(cls.pick, cls.product_b, 10)
        cls.pick.action_done()

        assert cls.pick.state == 'done'
        assert cls.delivery.state == 'assigned'

    def test_if_one_product_processed__return_picking_has_one_line(self):
        self.select_quantities(self.delivery, self.product_a, 10)
        picking = self.return_products()
        assert len(picking.move_lines) == 1
        assert picking.move_lines.product_id == self.product_b

    def test_if_one_product_partially_processed__return_picking_has_two_lines(self):
        self.select_quantities(self.delivery, self.product_a, 9)
        picking = self.return_products()
        assert len(picking.move_lines) == 2

    def test_if_returned_quantity_is_set_properly(self):
        self.select_quantities(self.delivery, self.product_a, 10)
        self.select_quantities(self.delivery, self.product_b, 6)
        picking = self.return_products()
        assert picking.move_lines.product_uom_qty == 4  # 10 - 6


class TestBackOrderOnFirstStep(StockReturnCase):
    """Test the case where the first step is completed with a backorder."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.select_quantities(cls.pick, cls.product_a, 5)
        cls.select_quantities(cls.pick, cls.product_b, 10)

        wizard_action = cls.pick.button_validate()
        wizard = cls.env['stock.backorder.confirmation'].browse(wizard_action['res_id'])
        wizard.process()

        cls.backorder = cls.env['stock.picking'].search([('backorder_id', '=', cls.pick.id)])
        cls.select_quantities(cls.backorder, cls.product_a, 5)
        cls.backorder.action_done()

        assert cls.pick.state == 'done'
        assert cls.backorder.state == 'done'
        assert cls.delivery.state == 'assigned'

    def test_if_one_product_processed__return_picking_has_one_line(self):
        self.select_quantities(self.delivery, self.product_b, 10)
        picking = self.return_products()
        assert len(picking.move_lines) == 1
        assert picking.move_lines.product_id == self.product_a
