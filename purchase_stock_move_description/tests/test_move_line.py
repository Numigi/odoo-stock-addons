# © 2023Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.purchase_stock.tests.test_create_picking import TestCreatePicking


class StockMoveTest(TestCreatePicking):

    def test_07_description_from_po_line_to_stock_picking_move_line(self):
        po = self.env['purchase.order'].create(self.po_vals)

        # Confirm the purchase order.
        po.button_confirm()

        picking = po.picking_ids[0]
        move = picking.move_lines[0]
        self.assertEqual(move.product_description, self.product_id_1.name)

        po_line = po.order_line[0]
        po_line.name = "Test new description"
        self.assertEqual(move.product_description, "Test new description")
