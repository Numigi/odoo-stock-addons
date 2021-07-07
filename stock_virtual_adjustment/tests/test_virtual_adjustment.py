# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class StockInventoryCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
            }
        )
        cls.uom = cls.product.uom_id

        cls.adjustment_date = datetime(2021, 1, 1)
        cls.reversal_date = datetime(2021, 1, 31)

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.company = cls.warehouse.company_id
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.adjustment_location = cls.env.ref("stock.location_inventory")

        cls.adjustment = cls.env["stock.virtual.adjustment"].create(
            {
                "company_id": cls.company.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.adjustment_location.id,
                "adjustment_date": cls.adjustment_date,
                "reversal_date": cls.reversal_date,
            }
        )

        cls.quantity = 10

        cls.line = cls.env["stock.virtual.adjustment.line"].create(
            {
                "adjustment_id": cls.adjustment.id,
                "product_id": cls.product.id,
                "quantity": cls.quantity,
                "uom_id": cls.uom.id,
            }
        )

    def test_confirm__stock_moves(self):
        self.adjustment.confirm()
        moves = self.adjustment.move_ids.sorted("date")
        assert len(moves) == 2
        assert moves[0].state == "done"
        assert moves[1].state == "done"

        assert moves[0].date == self.adjustment_date
        assert moves[1].date == self.reversal_date

        assert moves[0].location_id == self.stock_location
        assert moves[0].location_dest_id == self.adjustment_location

        assert moves[1].location_id == self.adjustment_location
        assert moves[1].location_dest_id == self.stock_location

        assert moves.mapped("product_id") == self.product
        assert moves.mapped("product_uom") == self.uom

        assert moves[0].product_uom_qty == self.quantity
        assert moves[1].product_uom_qty == self.quantity

        assert moves[0].origin == self.adjustment.name
        assert moves[1].origin == self.adjustment.name

    def test_confirm__no_picking_assigned(self):
        self.adjustment.confirm()
        moves = self.adjustment.move_ids
        assert not moves.mapped("picking_id")

    def test_confirm__negative_quantity(self):
        self.line.quantity = -1
        self.adjustment.confirm()
        moves = self.adjustment.move_ids.sorted("date")

        assert moves[1].location_id == self.stock_location
        assert moves[1].location_dest_id == self.adjustment_location

        assert moves[0].location_id == self.adjustment_location
        assert moves[0].location_dest_id == self.stock_location

        assert moves[0].product_uom_qty == 1
        assert moves[1].product_uom_qty == 1

    def test_confirm__adjustment_status(self):
        self.adjustment.confirm()
        assert self.adjustment.state == "done"

    def test_cancel(self):
        self.adjustment.cancel()
        assert self.adjustment.state == "cancelled"

    def test_cancel__done_adjustment(self):
        self.adjustment.confirm()
        with pytest.raises(ValidationError):
            self.adjustment.cancel()

    def test_set_to_draft(self):
        self.adjustment.cancel()
        self.adjustment.set_to_draft()
        assert self.adjustment.state == "draft"

    def test_set_to_draft__done_adjustment(self):
        self.adjustment.confirm()
        with pytest.raises(ValidationError):
            self.adjustment.set_to_draft()

    def test_confirm__with_fifo_valuation_method(self):
        self.product.categ_id.property_cost_method = "fifo"
        with pytest.raises(ValidationError):
            self.adjustment.confirm()

    def test_confirm__with_dates_in_future(self):
        self.adjustment.adjustment_date = datetime.now() + timedelta(1)
        self.adjustment.reversal_date = self.adjustment.adjustment_date + timedelta(1)
        with pytest.raises(ValidationError):
            self.adjustment.confirm()

    def test_confirm__with_reversal_prior_to_adjustment(self):
        self.adjustment.reversal_date = self.adjustment.adjustment_date - timedelta(1)
        with pytest.raises(ValidationError):
            self.adjustment.confirm()

    def test_copy(self):
        self.adjustment.confirm()
        adjustment = self.adjustment.copy()
        assert adjustment.state == "draft"
        assert len(adjustment.line_ids) == 1
        assert not adjustment.move_ids

    def test_stock_move_count(self):
        self.adjustment.confirm()
        assert self.adjustment.stock_move_count == 2

    def test_view_stock_moves(self):
        self.adjustment.confirm()
        action = self.adjustment.view_stock_moves()
        assert action["domain"] == [("id", "in", self.adjustment.move_ids.ids)]

    def test_onchange_product_set_uom(self):
        line = self.env["stock.virtual.adjustment.line"].new({})
        line.product_id = self.product
        line._onchange_product_id()
        assert line.uom_id == self.product.uom_id
