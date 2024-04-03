# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.stock_secondary_unit.tests.test_stock_secondary_unit import (
    TestProductSecondaryUnit,
)


class TestStockWarehouseOrderpoint(TestProductSecondaryUnit):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_product_replenishment(self):
        """
        Create replenishment order for white product on model stock.warehouse.orderpoint
        and test if all fields with secondary unit are calculated correctly.
        """
        replenishment_model = self.env["stock.warehouse.orderpoint"]
        # Create replenishment order for white product
        replenishment_order = replenishment_model.create(
            {
                "product_id": self.product_template.product_variant_ids[0].id,
                "warehouse_id": self.warehouse.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
            }
        )

        # Check secondary_uom_id.factor and product_uom.rounding are set correctly
        self.assertEqual(
            replenishment_order.secondary_uom_id,
            replenishment_order.product_tmpl_id.stock_secondary_uom_id,
        )
        self.assertEqual(
            replenishment_order.secondary_uom_id.factor,
            replenishment_order.product_tmpl_id.stock_secondary_uom_id.factor,
        )

        self.assertEqual(
            replenishment_order.secondary_uom_id.factor,
            0.5,
        )
        # Set qty_to_order to 20.0
        replenishment_order.qty_to_order = 20.0

        # Check if all fields with secondary unit are calculated correctly
        self.assertEqual(replenishment_order.secondary_uom_qty, 40.0)
        self.assertEqual(
            replenishment_order.secondary_uom_id,
            replenishment_order.product_tmpl_id.stock_secondary_uom_id,
        )
        # we have 10 initially on hand and 10 forecasted
        self.assertEqual(replenishment_order.secondary_uom_qty_on_hand, 20.0)
        self.assertEqual(replenishment_order.secondary_uom_qty_forecast, 20.0)

        # Check when secondary_uom_qty is changed, qty_to_order is also changed
        replenishment_order.secondary_uom_qty = 30.0
        self.assertEqual(replenishment_order.qty_to_order, 15.0)
