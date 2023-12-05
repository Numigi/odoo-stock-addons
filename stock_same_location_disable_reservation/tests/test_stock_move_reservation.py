# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockMoveReservation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveReservation, cls).setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Numigi Product",
                "type": "product",
                "sale_delay": 5,
                "uom_id": 1,
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_reservation_same_location(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.env.ref("stock.stock_location_stock"), 20
        )

        # Reservation could NOT pass
        picking1 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.location_dest.id,
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "name": "test_transit_1",
                "location_id": self.stock_location.id,
                "location_dest_id": self.location_dest.id,
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

        # Reservation could pass
        picking2 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move2 = self.env["stock.move"].create(
            {
                "name": "test_transit_2",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
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