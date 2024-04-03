# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestStockWarehouseOrderpoint(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.warehouse = cls.env.ref("stock.warehouse0")

        # Create product attribute and attribute value
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        cls.attribute_color = ProductAttribute.create({"name": "test_color"})
        cls.attribute_value_white = ProductAttributeValue.create(
            {"name": "test_white", "attribute_id": cls.attribute_color.id}
        )

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
                            "code": "A",
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    ),
                ],
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute_color.id,
                            "value_ids": [
                                (4, cls.attribute_value_white.id),
                            ],
                        },
                    )
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
        replenishment_order._compute_to_secondary_uom()
        replenishment_order.refresh()
        self.assertEqual(replenishment_order.qty_on_hand, 10.0)
        self.assertEqual(replenishment_order.secondary_uom_qty_on_hand, 20.0)
        self.assertEqual(replenishment_order.secondary_uom_qty_forecast, 20.0)

        # Check when secondary_uom_qty is changed, qty_to_order is also changed
        replenishment_order.secondary_uom_qty = 30.0
        self.assertEqual(replenishment_order.qty_to_order, 15.0)
