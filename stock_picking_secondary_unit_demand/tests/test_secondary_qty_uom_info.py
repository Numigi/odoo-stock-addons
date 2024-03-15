# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_order_secondary_unit.tests.test_sale_order_secondary_unit import (
    TestSaleOrderSecondaryUnit,
)


class TestSecondaryQtyUomInfo(TestSaleOrderSecondaryUnit):
    def setUp(self):
        super(TestSaleOrderSecondaryUnit, self).setUp()

    def test_secondary_qty_uom_info_on_stock_move(self):
        self.order.order_line.write(
            {"secondary_uom_qty": 2, "secondary_uom_id": self.secondary_unit.id})
        self.order.action_confirm()
        self.assertGreater(len(self.order.picking_ids.ids), 0, msg=None)
        if self.order.picking_ids:
            picking = self.order.picking_ids[0]
            for stock_move in picking.move_ids_without_package:
                self.assertEqual(
                    stock_move.merged_qty_uom_info, "2.00 unit-500")

    def test_secondary_qty_uom_info_on_stock_move_line(self):
        self.order.order_line.write(
            {"secondary_uom_qty": 3, "secondary_uom_id": self.secondary_unit.id})
        self.order.action_confirm()
        self.assertGreater(len(self.order.picking_ids.ids), 0, msg=None)
        if self.order.picking_ids:
            picking = self.order.picking_ids[0]
            for stock_move_line in picking.move_line_ids_without_package:
                self.assertEqual(
                    stock_move_line.merged_qty_uom_info, "3.00 unit-500")
