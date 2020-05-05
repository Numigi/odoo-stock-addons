# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.stock_picking_add_transit.tests.common import (
    StockPickingAddTransitCase,
)


class RentalAddTransitCase(StockPickingAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental_customer_location = cls.env.ref("stock_rental.customer_location")


class TestOutgoingPicking(RentalAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.make_picking(cls.stock_location, cls.rental_customer_location)
        cls.move_2 = cls.make_stock_move(cls.picking, cls.product_a, 2)
        cls.move_line = cls.make_stock_move_line(cls.move_2, 1)
        cls.move_2.state = "partially_available"
        cls.add_transit(cls.picking, cls.transit_1)
        cls.move_1 = cls.move_2.move_orig_ids

    def test_source_location(self):
        assert self.move_1.location_id == self.stock_location
        assert self.move_2.location_id == self.transit_1

    def test_destination_location(self):
        assert self.move_1.location_dest_id == self.transit_1
        assert self.move_2.location_dest_id == self.rental_customer_location


class TestIncomingPicking(RentalAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.make_picking(cls.rental_customer_location, cls.stock_location)
        cls.move_1 = cls.make_stock_move(cls.picking, cls.product_a, 2)
        cls.move_line = cls.make_stock_move_line(cls.move_1, 1)
        cls.move_1.state = "partially_available"
        cls.add_transit(cls.picking, cls.transit_1)
        cls.move_2 = cls.move_1.move_dest_ids

    def test_source_location(self):
        assert self.move_1.location_id == self.rental_customer_location
        assert self.move_2.location_id == self.transit_1

    def test_destination_location(self):
        assert self.move_1.location_dest_id == self.transit_1
        assert self.move_2.location_dest_id == self.stock_location
