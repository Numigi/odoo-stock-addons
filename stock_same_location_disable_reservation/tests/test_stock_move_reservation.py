# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockMoveReservation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveReservation, cls).setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.shelf1_location = cls.env["stock.location"].create(
            {
                "name": "shelf1",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.shelf2_location = cls.env["stock.location"].create(
            {
                "name": "shelf2",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.internal_operation = cls.env.ref("stock.picking_type_internal")
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Numigi Product",
                "type": "product",
                "sale_delay": 5,
                "uom_id": 1,
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_reservation_1(self):
        # Available quantity is on shelf1 only
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.shelf1_location, 20
        )

        # Reservation could NOT pass on shelf1 (same location as destination)
        picking1 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf1_location.id,
                "picking_type_id": self.internal_operation.id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "name": "test_transit_1",
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf1_location.id,
                "product_id": self.product1.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "picking_id": picking1.id,
            }
        )
        picking1.action_confirm()
        picking1.action_assign()

        # Picking and Move did not pass to the next step
        self.assertNotEqual(picking1.state, "assigned")
        self.assertNotEqual(move1.state, "partially_available")
        self.assertNotEqual(move1.state, "assigned")

        # Reservation could pass on shelf2 (different from destination)
        picking2 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf2_location.id,
                "picking_type_id": self.internal_operation.id,
            }
        )
        move2 = self.env["stock.move"].create(
            {
                "name": "test_transit_2",
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf2_location.id,
                "product_id": self.product1.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "picking_id": picking2.id,
            }
        )

        picking2.action_confirm()
        picking2.action_assign()
        self.assertEqual(picking2.state, "assigned")
        self.assertEqual(move2.state, "assigned")

    def test_reservation_2(
        self,
    ):
        # Available quantity is on shelf1
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.shelf1_location, 20
        )
        # Add available quantity on shelf2
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.shelf2_location, 20
        )

        picking1 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf1_location.id,
                "picking_type_id": self.internal_operation.id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "name": "test_transit_1",
                "location_id": self.stock_location.id,
                "location_dest_id": self.shelf1_location.id,
                "product_id": self.product1.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "picking_id": picking1.id,
            }
        )

        # This could pass now
        picking1.action_confirm()
        picking1.action_assign()
        self.assertEqual(picking1.state, "assigned")
        self.assertEqual(move1.state, "assigned")
