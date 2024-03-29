# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductCategoryRestrictions(TransactionCase):
    def setUp(self):
        super(TestProductCategoryRestrictions, self).setUp()
        ResCompany = self.env['res.company']
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.company_a = ResCompany.create({
            'name': 'Company Test A',
            'currency_id': self.env.ref('base.USD').id,
        })
        self.company_b = ResCompany.create({
            'name': 'Company Test B',
            'currency_id': self.env.ref('base.USD').id,
        })

        # Stock location for company A
        customer_loc = self.env.ref(
            'stock.stock_location_customers', raise_if_not_found=False)
        self.stock_location_a = self.env['stock.location'].with_company(self.company_a).create({
            'name': "Stock Location A",
            'location_id': customer_loc.id,
        })

        self.product = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.env.user.write({
            'company_id': self.company_a.id,
            'company_ids': [(6, 0, [self.company_a.id, self.company_b.id])]
        })

    def test_change_product_category_on_product_with_stock_move(self):
        # company A
        self.process_stock_move(self.company_a, self.stock_location_a)
        self.assert_on_product()

        # company B
        self.env.user.company_id = self.company_b.id
        self.assert_on_product()

    def test_update_product_category_with_stock_move(self):
        """
        Tests on these fields if changed :
        - property_stock_account_input_categ_id
        - property_stock_account_output_categ_id
        - property_stock_valuation_account_id
        - property_stock_journal
        """
        # company A
        self.env.user.company_id = self.company_a.id
        move = self.process_stock_move(self.company_a, self.stock_location_a)
        categ_all = self.env.ref('product.product_category_all')

        domain = [("product_id.categ_id", "in", categ_all.ids)]
        existing_move_lines = self.env["stock.move.line"].search(domain)
        not_allowed = categ_all._multi_company_constraints(
            existing_move_lines)

        self.assertGreater(len(existing_move_lines), 0)
        self.assertTrue(not_allowed)
        self.assertEqual(move.company_id, self.env.user.company_id)

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

        # changing to company B then all changes are allowed
        # because stock move is linked to company A
        self.env.user.company_id = self.company_b.id
        categ_all.write(
            {
                'property_stock_account_input_categ_id': False,
                'property_stock_account_output_categ_id': False,
                'property_stock_valuation_account_id': False,
                'property_stock_journal': False
            })

    def assert_on_product(self):
        # for product.product
        with self.assertRaises(UserError):
            self.product.write(
                {'categ_id': self.env.ref('product.product_category_1').id})

        # for product.template
        with self.assertRaises(UserError):
            self.product.product_tmpl_id.write(
                {'categ_id': self.env.ref('product.product_category_1').id})

    def process_stock_move(self, company_id, stock_location_id):
        move = self.env['stock.move'].create({
            'name': 'new_move',
            'location_id': stock_location_id.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'company_id': company_id.id,
        })
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.write({'qty_done': 1.0})
        move._action_done()
        lot = self.env['stock.production.lot'].create({
            'name': 'lot for test',
            'product_id': self.product.id,
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
        return move
