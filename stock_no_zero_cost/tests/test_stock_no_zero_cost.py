# # -*- coding: utf-8 -*-
# from odoo.tests.common import TransactionCase
# from odoo.exceptions import UserError
#
#
# class TestStockNoZeroCost(TransactionCase):
#
#     def setUp(self):
#         super(TestStockNoZeroCost, self).setUp()
#
#         # 1. Configuration des utilisateurs
#         self.standard_user = self.env['res.users'].create({
#             'name': 'Standard Warehouse User',
#             'login': 'standard_user_test',
#             'groups_id': [(6, 0, [
#                 self.env.ref('base.group_user').id,
#                 self.env.ref('stock.group_stock_user').id,
#                 self.env.ref('mrp.group_mrp_user').id
#             ])]
#         })
#
#         self.manager_user = self.env['res.users'].create({
#             'name': 'Warehouse Manager (Bypass)',
#             'login': 'manager_user_test',
#             'groups_id': [(6, 0, [
#                 self.env.ref('base.group_user').id,
#                 self.env.ref('stock.group_stock_manager').id,
#                 self.env.ref('mrp.group_mrp_manager').id,
#                 self.env.ref('stock_no_zero_cost.group_allow_zero_cost_move').id  # Le droit de Bypass
#             ])]
#         })
#
#         # 2. Configuration des Articles
#         self.product_zero = self.env['product.product'].create({
#             'name': 'Test Product Zero Cost',
#             'type': 'product',
#             'standard_price': 0.0,
#         })
#
#         self.product_price = self.env['product.product'].create({
#             'name': 'Test Product With Cost',
#             'type': 'product',
#             'standard_price': 15.0,
#         })
#
#         # 3. Configuration des Emplacements
#         self.supplier_loc = self.env.ref('stock.stock_location_suppliers')
#         self.stock_loc = self.env.ref('stock.stock_location_stock')
#         self.customer_loc = self.env.ref('stock.stock_location_customers')
#
#     def _create_picking(self, location_id, location_dest_id, product, price_unit=0.0):
#         """Helper for creating a stock picking."""
#         picking_type = self.env['stock.picking.type'].search([
#             ('default_location_src_id', '=', location_id.id),
#             ('default_location_dest_id', '=', location_dest_id.id),
#         ], limit=1)
#
#         if not picking_type:
#             picking_type = self.env.ref('stock.picking_type_internal')
#
#         picking = self.env['stock.picking'].create({
#             'location_id': location_id.id,
#             'location_dest_id': location_dest_id.id,
#             'picking_type_id': picking_type.id,
#         })
#
#         move = self.env['stock.move'].create({
#             'name': product.name,
#             'product_id': product.id,
#             'product_uom_qty': 1.0,
#             'product_uom': product.uom_id.id,
#             'picking_id': picking.id,
#             'location_id': location_id.id,
#             'location_dest_id': location_dest_id.id,
#             'price_unit': price_unit,
#         })
#         picking.action_confirm()
#         move.quantity_done = 1.0
#         return picking
#
#     def test_01_standard_user_blocked_on_zero_cost_in(self):
#         """TEST 1: Standard user gets a hard block (UserError) on Receipt with 0 cost."""
#         picking = self._create_picking(self.supplier_loc, self.stock_loc, self.product_zero, price_unit=0.0)
#
#         with self.assertRaises(UserError):
#             picking.with_user(self.standard_user).button_validate()
#
#     def test_02_manager_user_wizard_bypass_on_zero_cost_in(self):
#         """TEST 2: Manager user gets the wizard, confirms it, and the transfer is validated with a trace."""
#         picking = self._create_picking(self.supplier_loc, self.stock_loc, self.product_zero, price_unit=0.0)
#
#         # 1. The manager clicks validate -> should return an action dictionary (the wizard)
#         action = picking.with_user(self.manager_user).button_validate()
#
#         self.assertEqual(type(action), dict, "Expected an action dictionary to open the wizard.")
#         self.assertEqual(action.get('res_model'), 'stock.zero.cost.wizard', "Expected the Zero Cost Wizard.")
#
#         # 2. Simulate the Wizard creation and confirmation
#         wizard_context = action.get('context', {})
#         wizard = self.env['stock.zero.cost.wizard'].with_user(self.manager_user).with_context(**wizard_context).create(
#             {})
#         wizard.action_confirm()
#
#         # 3. Check results
#         self.assertEqual(picking.state, 'done', "Picking should be validated after wizard confirmation.")
#
#         # 4. Check Traceability
#         done_move = picking.move_lines[0]
#         self.assertTrue(done_move.zero_cost_approval_note, "Traceability note should be stamped on the stock move.")
#         self.assertIn("Action Forced", done_move.zero_cost_approval_note)
#
#     def test_03_standard_user_can_ship_out_zero_cost(self):
#         """TEST 3: Standard user can validate a Delivery (OUT) even if cost is 0."""
#         picking = self._create_picking(self.stock_loc, self.customer_loc, self.product_zero)
#
#         # Should not raise any error, goes straight to done (or backorder wizard normally, but here we fulfill all qty)
#         res = picking.with_user(self.standard_user).button_validate()
#         if res is True or res is None:
#             self.assertEqual(picking.state, 'done')
#
#     def test_04_mrp_production_zero_cost_manager(self):
#         """TEST 4: MRP Production triggers the wizard for managers."""
#         # Create an empty Manufacturing Order
#         mo = self.env['mrp.production'].create({
#             'product_id': self.product_zero.id,
#             'product_qty': 1.0,
#             'product_uom_id': self.product_zero.uom_id.id,
#         })
#         mo.action_confirm()
#         mo.qty_producing = 1.0
#
#         # Manager clicks Mark as Done
#         action = mo.with_user(self.manager_user).button_mark_done()
#
#         # Should trigger the wizard
#         self.assertEqual(type(action), dict)
#         self.assertEqual(action.get('res_model'), 'stock.zero.cost.wizard')
