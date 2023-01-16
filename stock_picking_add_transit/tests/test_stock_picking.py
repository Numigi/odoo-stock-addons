# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from .common import StockPickingAddTransitCase


class TestOutgoingPicking(StockPickingAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.make_quant(cls.stock_location, cls.product_a, 1)
        cls.picking = cls.make_picking(cls.stock_location, cls.customer_location)
        cls.move_3 = cls.make_stock_move(cls.picking, cls.product_a, 2)
        cls.picking.action_assign()
        cls.move_line = cls.move_3.move_line_ids
        cls.move_line.qty_done = 1
        cls.add_transit(cls.picking, cls.transit_1)
        cls.add_transit(cls.picking, cls.transit_2)
        cls.move_2 = cls.move_3.move_orig_ids
        cls.move_1 = cls.move_2.move_orig_ids

    def test_picking_origin(self):
        assert self.move_1.picking_id.origin == self.picking.name
        assert self.move_2.picking_id.origin == self.picking.name

    def test_transit_partner_type(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "stock_picking_add_transit.transit_partner_type", 'warehouse')
        assert self.move_1.picking_id.partner_id == self.warehouse.partner_id

    def test_source_location(self):
        assert self.move_1.location_id == self.stock_location
        assert self.move_2.location_id == self.transit_1
        assert self.move_3.location_id == self.transit_2

    def test_destination_location(self):
        assert self.move_1.location_dest_id == self.transit_1
        assert self.move_2.location_dest_id == self.transit_2
        assert self.move_3.location_dest_id == self.customer_location

    def test_stock_move_line(self):
        self.move_1.refresh()
        assert self.move_line.move_id == self.move_1
        assert self.move_line.picking_id == self.move_1.picking_id
        assert self.move_line.location_id == self.stock_location
        assert self.move_line.location_dest_id == self.transit_1

    def test_stock_move_state(self):
        assert self.move_1.state == "partially_available"
        assert self.move_2.state == "waiting"
        assert self.move_3.state == "waiting"

    def test_process_stock_move(self):
        self.move_1.picking_id.action_done()
        assert self.move_1.state == "done"
        assert self.move_2.state == "partially_available"
        assert self.move_3.state == "waiting"


class TestIncomingPicking(StockPickingAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.make_picking(cls.customer_location, cls.stock_location)
        cls.move_1 = cls.make_stock_move(cls.picking, cls.product_a, 2)
        cls.move_line = cls.make_stock_move_line(cls.move_1, 1)
        cls.move_1.state = "partially_available"
        cls.add_transit(cls.picking, cls.transit_2)
        cls.add_transit(cls.picking, cls.transit_1)
        cls.move_2 = cls.move_1.move_dest_ids
        cls.move_3 = cls.move_2.move_dest_ids

    def test_picking_origin(self):
        assert self.move_2.picking_id.origin == self.picking.name
        assert self.move_3.picking_id.origin == self.picking.name

    def test_source_location(self):
        assert self.move_1.location_id == self.customer_location
        assert self.move_2.location_id == self.transit_1
        assert self.move_3.location_id == self.transit_2

    def test_destination_location(self):
        assert self.move_1.location_dest_id == self.transit_1
        assert self.move_2.location_dest_id == self.transit_2
        assert self.move_3.location_dest_id == self.stock_location

    def test_stock_move_line(self):
        assert self.move_line.move_id == self.move_1
        assert self.move_line.location_id == self.customer_location
        assert self.move_line.location_dest_id == self.transit_1

    def test_stock_move_state(self):
        assert self.move_1.state == "partially_available"
        assert self.move_2.state == "waiting"
        assert self.move_3.state == "waiting"


class TestDropshipPicking(StockPickingAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.make_picking(cls.supplier_location, cls.customer_location)
        cls.picking.picking_type_id = cls.env.ref(
            "stock_dropshipping.picking_type_dropship"
        )
        cls.move_1 = cls.make_stock_move(cls.picking, cls.product_a, 2)
        cls.move_line = cls.make_stock_move_line(cls.move_1, 1)
        cls.move_1.state = "partially_available"
        cls.add_transit(cls.picking, cls.transit_2)
        cls.add_transit(cls.picking, cls.transit_1)
        cls.move_2 = cls.move_1.move_dest_ids
        cls.move_3 = cls.move_2.move_dest_ids

    def test_source_location(self):
        assert self.move_1.location_id == self.supplier_location
        assert self.move_1.location_dest_id == self.transit_1
        assert self.move_2.location_id == self.transit_1
        assert self.move_2.location_dest_id == self.transit_2
        assert self.move_3.location_id == self.transit_2
        assert self.move_3.location_dest_id == self.customer_location


class TestConstraints(StockPickingAddTransitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.make_picking(cls.stock_location, cls.customer_location)
        cls.move_3 = cls.make_stock_move(cls.picking, cls.product_a, 2)

    def test_if_picking_is_draft__raise_error(self):
        with pytest.raises(ValidationError):
            self.add_transit(self.picking, self.transit_1)

    def test_if_picking_is_done__raise_error(self):
        self.make_stock_move_line(self.move_3, 1)
        self.picking.action_done()
        with pytest.raises(ValidationError):
            self.add_transit(self.picking, self.transit_1)

    def test_if_picking_is_cancelled__raise_error(self):
        self.picking.action_cancel()
        with pytest.raises(ValidationError):
            self.add_transit(self.picking, self.transit_1)
