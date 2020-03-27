# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime

import pytest

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestStockPickingLocationDestination(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location3 = cls.env.ref("stock.stock_location_3")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env.ref("stock.incomming_shipment")
        cls.picking_location3 = cls.picking.copy()
        cls.picking_location3.location_dest_id = cls.location3.id
        cls.picking_moves_destination_moves = cls.picking.copy()
        cls.picking_moves_destination_moves.move_lines.write({
            "move_dest_ids": [(6, 0, [cls.location_customers.id])]
        })

    def test_whenNewLocationIsSet_thenPickingLocationChanges(self):
        assert self.location3 != self.picking.location_dest_id
        self.picking.set_location_destination(self.location3)
        assert self.location3 == self.picking.location_dest_id

    def test_whenLocationIsTheSame_thenPickingStays(self):
        assert self.location3 == self.picking_location3.location_dest_id
        self.picking.set_location_destination(self.location3)
        assert self.location3 == self.picking_location3.location_dest_id

    def test_whenNewLocationIsSet_thenMovesLocationsChange(self):
        self.picking.set_location_destination(self.location3)
        assert all(
            self.location3 == move.location_dest_id
            for move in self.picking.move_lines
        )

    def test_whenMovesHaveDestinationMoves_thenRaiseError(self):
        with pytest.raises(UserError):
            self.picking_moves_destination_moves.set_location_destination(self.location3)
