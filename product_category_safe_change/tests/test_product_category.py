# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.test_move import StockMove
from odoo.exceptions import UserError


class TestProductCategoryRestrictions(StockMove):
    def setUp(self):
        super(TestProductCategoryRestrictions, self).setUp()

    def test_change_product_category_on_product_with_stock_move(self):
        self.process_stock_move()
        # for product.product
        with self.assertRaises(UserError):
            self.product2.write(
                {'categ_id': self.env.ref('product.product_category_1').id})

        # for product.template
        with self.assertRaises(UserError):
            self.product2.product_tmpl_id.write(
                {'categ_id': self.env.ref('product.product_category_1').id})

    def test_update_product_category_with_stock_move(self):
        """
        Tests on these fields if changed :
        - property_stock_account_input_categ_id
        - property_stock_account_output_categ_id
        - property_stock_valuation_account_id
        - property_stock_journal
        """
        self.process_stock_move()
        categ_all = self.env.ref('product.product_category_all')

        # for property_stock_account_input_categ_id
        with self.assertRaises(UserError):
            categ_all.write(
                {'property_stock_account_input_categ_id': False})

        # for property_stock_account_output_categ_id
        with self.assertRaises(UserError):
            categ_all.write(
                {'property_stock_account_output_categ_id': False})

        # for property_stock_valuation_account_id
        with self.assertRaises(UserError):
            categ_all.write(
                {'property_stock_valuation_account_id': False})

        # for property_stock_journal
        with self.assertRaises(UserError):
            categ_all.write(
                {'property_stock_journal': False})

    def process_stock_move(self):
        move = self.env['stock.move'].create({
            'name': 'new_move',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
        })
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.write({'qty_done': 1.0})
        move._action_done()
        lot = self.env['stock.production.lot'].create({
            'name': 'lot for test',
            'product_id': self.product2.id,
        })

        self.env['stock.move.line'].create({
            'move_id': move.id,
            'product_id': move.product_id.id,
            'qty_done': 1,
            'product_uom_id': move.product_uom.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'lot_id': lot.id,
        })
