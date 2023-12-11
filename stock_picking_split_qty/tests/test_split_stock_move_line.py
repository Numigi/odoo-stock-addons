# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.test_move import StockMove as StockMove


class TestSplitStockMoveLine(StockMove):
    def setUp(self):
        super(StockMove, self).setUp()

    def test_split_move_line_outgoing_picking(self):
        """Check that reserving a move and spliting its move lines to
        different lines work as expected.
        """
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 50
        )
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )

        self.env["stock.move"].create(
            {
                "name": "test_transit_1",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "picking_id": picking.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")

        # Initially, on picking, we have only one line of move line
        self.assertEqual(len(picking.move_line_ids), 1)

        # Make for firt stock move quanity for 2 (we have to do 10)
        picking.move_lines[0].move_line_ids[0].qty_done = 2.0

        # ... then do SPLIT
        picking.action_divide_stock_move_line()

        # Move line on picking becomes 2
        self.assertEqual(len(picking.move_line_ids), 2)
        # Move line on picking becomes 2 linked to move
        self.assertEqual(len(picking.move_lines[0].move_line_ids), 2)
        # Quantity done on the second newly created move line is 2
        self.assertEqual(picking.move_line_ids[1].qty_done, 2)
        # Quantity on initial stock move will be reduced by 2, so now 10 - 2 = 8
        self.assertEqual(picking.move_lines[0].move_line_ids[0].product_uom_qty, 8)

        # Make for firt stock move quanity for 4 (we have to do 8 now, previously changed)
        picking.move_lines[0].move_line_ids[0].qty_done = 4.0

        # ... then do SPLIT again
        picking.action_divide_stock_move_line()

        # Move line on picking becomes 3
        self.assertEqual(len(picking.move_line_ids), 3)
        # Move line on picking becomes 3 linked to move
        self.assertEqual(len(picking.move_lines[0].move_line_ids), 3)
        # Quantity done on the third newly created move line is 4
        self.assertEqual(picking.move_line_ids[2].qty_done, 4)
        # Quantity on initial stock move will be reduced by 4, so now 8 - 4 = 4
        self.assertEqual(picking.move_lines[0].move_line_ids[0].product_uom_qty, 4)
