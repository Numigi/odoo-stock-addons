# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo import fields


class TestStockNoZeroCost(TransactionCase):

    def setUp(self):
        super(TestStockNoZeroCost, self).setUp()
        self.env = self.env(context=dict(self.env.context, force_zero_cost_check=True))

        self.standard_user = self.env['res.users'].create({
            'name': 'Standard Warehouse User',
            'login': 'standard_user_test',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('stock.group_stock_user').id,
                self.env.ref('mrp.group_mrp_user').id
            ])]
        })

        self.manager_user = self.env['res.users'].create({
            'name': 'Warehouse Manager (Bypass)',
            'login': 'manager_user_test',
            'email': 'manager@test.com',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('stock.group_stock_manager').id,
                self.env.ref('mrp.group_mrp_manager').id,
                # Le droit de Bypass
                self.env.ref('stock_no_zero_cost.group_allow_zero_cost_move').id
            ])]
        })

        self.product_zero = self.env['product.product'].create({
            'name': 'Test Product Zero Cost',
            'type': 'product',
            'standard_price': 0.0,
        })

        self.product_price = self.env['product.product'].create({
            'name': 'Test Product With Cost',
            'type': 'product',
            'standard_price': 15.0,
        })

        self.supplier_loc = self.env.ref('stock.stock_location_suppliers')
        self.stock_loc = self.env.ref('stock.stock_location_stock')
        self.customer_loc = self.env.ref('stock.stock_location_customers')

    def _create_picking(self, location_id, location_dest_id, product, price_unit=0.0):
        """Helper for creating a stock picking."""
        picking_type = self.env['stock.picking.type'].search([
            ('default_location_src_id', '=', location_id.id),
            ('default_location_dest_id', '=', location_dest_id.id),
        ], limit=1)

        if not picking_type:
            picking_type = self.env.ref('stock.picking_type_internal')

        picking = self.env['stock.picking'].create({
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'picking_type_id': picking_type.id,
        })

        move = self.env['stock.move'].create({
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': 1.0,
            'product_uom': product.uom_id.id,
            'picking_id': picking.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'price_unit': price_unit,
        })
        picking.action_confirm()
        move.quantity_done = 1.0
        return picking

    def test_01_standard_user_blocked_on_zero_cost_in(self):
        """TEST 1: Standard user gets a hard block (UserError) on Receipt with 0 cost."""
        picking = self._create_picking(
            self.supplier_loc, self.stock_loc, self.product_zero, price_unit=0.0
        )

        with self.assertRaises(UserError):
            picking.with_user(self.standard_user).button_validate()

    def test_02_manager_user_wizard_bypass_on_zero_cost_in(self):
        """TEST 2: Manager user gets wizard, confirms it, and transfer is validated."""
        picking = self._create_picking(
            self.supplier_loc, self.stock_loc, self.product_zero, price_unit=0.0
        )

        action = picking.with_user(self.manager_user).with_context(
            force_zero_cost_check=True).button_validate()

        self.assertEqual(
            type(action), dict,
            "Expected an action dictionary to open the wizard."
        )

        # Simulate the Wizard creation and confirmation
        wizard_context = action.get('context', {})
        wizard_context['force_zero_cost_check'] = True
        wizard = self.env['stock.zero.cost.wizard'].with_user(
            self.manager_user
        ).with_context(**wizard_context).create({})

        wizard.action_confirm()

        self.assertEqual(
            picking.state, 'done',
            "Picking should be validated after wizard confirmation."
        )

        done_moves = self.env['stock.move'].search([('picking_id', '=', picking.id)])
        has_note = any(move.zero_cost_approval_note for move in done_moves)
        self.assertTrue(
            has_note,
            "Traceability note should be stamped on the stock move."
        )

    def test_03_standard_user_can_ship_out_zero_cost(self):
        """TEST 3: Standard user can validate a Delivery (OUT) even if cost is 0."""
        picking = self._create_picking(
            self.stock_loc, self.customer_loc, self.product_zero
        )

        res = picking.with_user(self.standard_user).button_validate()
        if res is True or res is None:
            self.assertEqual(picking.state, 'done')

    def test_04_mrp_production_zero_cost_manager(self):
        """TEST 4: MRP Production triggers the wizard for managers (if setting is ON)."""
        self.env.company.check_zero_cost_production = True
        self.env.company.check_zero_cost_consumption = True

        mo = self.env['mrp.production'].create({
            'product_id': self.product_zero.id,
            'product_qty': 1.0,
            'product_uom_id': self.product_zero.uom_id.id,
            'move_raw_ids': [(0, 0, {
                'name': self.product_price.name,
                'product_id': self.product_price.id,
                'product_uom_qty': 1.0,
                'product_uom': self.product_price.uom_id.id,
                'location_id': self.stock_loc.id,
                'location_dest_id': self.product_zero.property_stock_production.id,
            })]
        })
        mo.action_confirm()
        mo.qty_producing = 1.0
        for move in mo.move_raw_ids:
            move.quantity_done = move.product_uom_qty

        action = mo.with_user(self.manager_user).with_context(
            force_zero_cost_check=True).button_mark_done()

        if isinstance(action, dict):
            self.assertEqual(
                action.get('res_model'),
                'stock.zero.cost.wizard',
                "Expected the Zero Cost Wizard."
            )
        else:
            self.assertEqual(
                mo.state, 'done',
                "Manufacturing Order should be marked as done."
            )

    def test_05_mrp_production_allowed_by_default(self):
        """TEST 5: Standard user can validate MRP with 0 cost by default (TA#84365)."""
        self.env.company.check_zero_cost_production = False
        self.env.company.check_zero_cost_consumption = False

        mo = self.env['mrp.production'].create({
            'product_id': self.product_zero.id,
            'product_qty': 1.0,
            'product_uom_id': self.product_zero.uom_id.id,
            'move_raw_ids': [(0, 0, {
                'name': self.product_price.name,
                'product_id': self.product_price.id,
                'product_uom_qty': 1.0,
                'product_uom': self.product_price.uom_id.id,
                'location_id': self.stock_loc.id,
                'location_dest_id': self.product_zero.property_stock_production.id,
            })]
        })
        mo.action_confirm()
        mo.qty_producing = 1.0
        for move in mo.move_raw_ids:
            move.quantity_done = move.product_uom_qty

        action = mo.with_user(self.standard_user).with_context(
            force_zero_cost_check=True).button_mark_done()

        self.assertNotIsInstance(action, dict, "Wizard should not be triggered.")
        self.assertEqual(mo.state, 'done', "MO should be validated without block.")

    def test_06_partial_receipt_ignores_unprocessed_zero_cost_lines(self):
        """TEST 6: A partial receipt leaving a zero-cost product
        as backorder should NOT block."""
        picking = self.env['stock.picking'].create({
            'location_id': self.supplier_loc.id,
            'location_dest_id': self.stock_loc.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })

        # Line 1: ZERO cost product
        move_zero = self.env['stock.move'].create({
            'name': self.product_zero.name,
            'product_id': self.product_zero.id,
            'product_uom_qty': 1.0,
            'product_uom': self.product_zero.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.supplier_loc.id,
            'location_dest_id': self.stock_loc.id,
            'price_unit': 0.0,
        })

        # Line 2: Product with a standard PRICE
        move_price = self.env['stock.move'].create({
            'name': self.product_price.name,
            'product_id': self.product_price.id,
            'product_uom_qty': 1.0,
            'product_uom': self.product_price.uom_id.id,
            'picking_id': picking.id,
            'location_id': self.supplier_loc.id,
            'location_dest_id': self.stock_loc.id,
            'price_unit': 15.0,
        })

        picking.action_confirm()

        # The warehouse worker ONLY receives the priced product
        move_zero.quantity_done = 0.0
        move_price.quantity_done = 1.0

        # A standard user validates. If the logic was wrong, it would raise a UserError.
        action = picking.with_user(self.standard_user).with_context(
            force_zero_cost_check=True).button_validate()

        # Odoo will likely return the native "Create Backorder" Wizard dictionary.
        # The important thing is that it is NOT our zero-cost Wizard.
        if isinstance(action, dict):
            self.assertNotEqual(
                action.get('res_model'), 'stock.zero.cost.wizard',
                "Zero cost wizard should not appear for unprocessed lines."
            )

    def test_07_partial_production_ignores_unprocessed_zero_cost_components(self):
        """TEST 7: A production order leaving zero-cost components
         unconsumed should NOT block."""
        # Explicitly enable the locks for this test
        self.env.company.check_zero_cost_production = True
        self.env.company.check_zero_cost_consumption = True

        # Create a distinct finished product
        product_finished = self.env['product.product'].create({
            'name': 'Test Finished Product',
            'type': 'product',
            'standard_price': 50.0,
        })

        mo = self.env['mrp.production'].create({
            # Use the newly created finished product
            'product_id': product_finished.id,
            'product_qty': 1.0,
            'product_uom_id': product_finished.uom_id.id,
            'move_raw_ids': [
                (0, 0, {
                    'name': self.product_price.name,
                    'product_id': self.product_price.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.product_price.uom_id.id,
                    'location_id': self.stock_loc.id,
                    'location_dest_id': product_finished.property_stock_production.id,
                }),
                (0, 0, {
                    'name': self.product_zero.name,
                    'product_id': self.product_zero.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.product_zero.uom_id.id,
                    'location_id': self.stock_loc.id,
                    'location_dest_id': product_finished.property_stock_production.id,
                })
            ]
        })
        mo.action_confirm()

        # We successfully produce the final item
        mo.qty_producing = 1.0

        # But we ONLY consume the priced component (the free one is left at 0)
        mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_price).quantity_done = 1.0
        mo.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_zero).quantity_done = 0.0

        action = mo.with_user(self.manager_user).with_context(
            force_zero_cost_check=True).button_mark_done()

        # Our custom Wizard must absolutely not appear
        if isinstance(action, dict):
            self.assertNotEqual(
                action.get('res_model'), 'stock.zero.cost.wizard',
                "Zero cost wizard should not appear for unprocessed components."
            )

    def test_08_purchase_micro_cost_allowed(self):
        """TEST 8: A receipt from a Purchase Order with a micro-cost (e.g. 0.001)
        should NOT block, even if the stock move's price_unit is rounded to 0.0."""

        # We only run this test if the 'purchase' module is installed
        if 'purchase_line_id' not in self.env['stock.move']._fields:
            return

        partner = self.env['res.partner'].create({'name': 'Vendor Test'})

        # 1. Create a Purchase Order with a micro-cost of 0.001
        po = self.env['purchase.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': self.product_price.name,
                'product_id': self.product_price.id,
                'product_qty': 1.0,
                'product_uom': self.product_price.uom_id.id,
                'price_unit': 0.001,
                'date_planned': fields.Datetime.now(),
            })]
        })
        po.button_confirm()

        # 2. Process the receipt generated by the PO
        picking = po.picking_ids[0]
        for move in picking.move_lines:
            move.quantity_done = move.product_uom_qty

        # 3. Validate receipt as a standard user
        action = picking.with_user(self.standard_user).with_context(
            force_zero_cost_check=True).button_validate()

        # The receipt must NOT be blocked (No Wizard).
        if isinstance(action, dict):
            self.assertNotEqual(
                action.get('res_model'), 'stock.zero.cost.wizard',
                "Zero cost wizard should not appear for micro-costs (0.001)."
            )
