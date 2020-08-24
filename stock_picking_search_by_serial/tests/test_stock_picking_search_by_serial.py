# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestStockPickingSearchBySerial(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        stock_picking = cls.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            }
        )
        stock_move = cls.env["stock.move"].create(
            {
                "name": "stock move",
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "product_id": product.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1.0,
                "picking_id": stock_picking.id,
            }
        )
        cls.env["stock.move.line"].create(
            {
                "lot_name": "Right Lot",
                "move_id": stock_move.id,
                "product_id": product.id,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
            }
        )

    def _check_search_stock_picking_by_serial(self, serial, exist_result):
        res = self.env["stock.picking"].search(
            [("move_ids_without_package.move_line_ids.lot_name", "=", serial)]
        )
        if exist_result:
            self.assertEqual(len(res), 1)
        else:
            self.assertEqual(len(res), 0)

    def test_search_stock_picking_by_serial_with_result(self):
        self._check_search_stock_picking_by_serial(
            serial="Right Lot", exist_result=True
        )

    def test_search_stock_picking_by_serial_without_result(self):
        self._check_search_stock_picking_by_serial(
            serial="Wrong Lot", exist_result=False
        )
