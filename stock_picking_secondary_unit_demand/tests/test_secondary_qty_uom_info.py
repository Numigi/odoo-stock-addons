# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from odoo.addons.sale_order_secondary_unit.tests.test_sale_order_secondary_unit import (
    TestSaleOrderSecondaryUnit,
)


class TestSecondaryQtyUomInfo(TestSaleOrderSecondaryUnit):
    def setUp(self):
        super(TestSaleOrderSecondaryUnit, self).setUp()

    def test_secondary_qty_uom_info_on_stock_move(self):
        self.order.order_line.write(
            {"secondary_uom_qty": 2.00, "secondary_uom_id": self.secondary_unit.id}
        )
        self.order.action_confirm()
        self.assertGreater(len(self.order.picking_ids.ids), 0, msg=None)
        if self.order.picking_ids:
            picking = self.order.picking_ids[0]
            for stock_move in picking.move_ids_without_package:
                self.assertEqual(stock_move.merged_qty_uom_info, "2.00 unit-500")

    def test_secondary_qty_uom_info_on_stock_move_line(self):
        self.order.order_line.write(
            {"secondary_uom_qty": 3.00, "secondary_uom_id": self.secondary_unit.id}
        )
        self.order.action_confirm()
        self.assertGreater(len(self.order.picking_ids.ids), 0, msg=None)
        if self.order.picking_ids:
            picking = self.order.picking_ids[0]
            for stock_move_line in picking.move_line_ids_without_package:
                self.assertEqual(stock_move_line.merged_qty_uom_info, "3.00 unit-500")


class TestSimplePickingSecondaryQtyUomInfo(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.warehouse = cls.env.ref("stock.warehouse0")

        # Create product and configure
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "type": "product",
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "code": "U50",
                            "name": "unit-50",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.05,
                        },
                    ),
                ],
            }
        )
        # Select the first secondary unit found
        secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_template.id)], limit=1
        )
        cls.product_template.write({"stock_secondary_uom_id": secondary_unit.id})

        # Initialize quant for white product
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_template.product_variant_ids[0],
            cls.warehouse.lot_stock_id,
            10.0,
        )
