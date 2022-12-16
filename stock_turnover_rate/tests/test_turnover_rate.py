# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from ddt import data, ddt, unpack
from freezegun import freeze_time
from odoo.tests import common
from ..models.product import MAX_TURNOVER_RATE


@ddt
class TestTurnoverRate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.yesterday = datetime.now().date() - timedelta(1)

        cls.product = cls.env['product.product'].create({
            'name': 'My Product',
            'type': 'product',
        })

        cls.stock_location = cls.env.ref('stock.stock_location_stock')

        cls.customer_location = cls.env.ref('stock.stock_location_customers')

        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')

    def _create_quant(self, quantity, location=None):
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'quantity': quantity,
            'location_id': (location or self.stock_location).id,
        })

    def _create_stock_move(self, quantity, origin, destination):
        return self.env['stock.move'].create({
            'name': '/',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': quantity,
            'location_id': origin.id,
            'location_dest_id': destination.id,
        })

    def _process_stock_move(self, move, quantity):
        move._action_confirm()
        move.quantity_done = quantity
        move._action_done()
        assert move.state == 'done'

    def _receive(self, quantity):
        move = self._create_stock_move(quantity, self.supplier_location, self.stock_location)
        self._process_stock_move(move, quantity)

    def _deliver(self, quantity):
        move = self._create_stock_move(quantity, self.stock_location, self.customer_location)
        self._process_stock_move(move, quantity)

    def test_no_quant__no_move__then_turnover_is_zero(self):
        self.product.turnover_rate = 1
        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == 0

    def test_one_quant__no_move__then_turnover_is_zero(self):
        self.product.turnover_rate = 1
        self._create_quant(1)
        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == 0

    def test_stock_move_done_today_are_excluded(self):
        self.product.turnover_rate = 1
        self._create_quant(1)
        self._deliver(1)
        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == 0

    def test_stock_move_done_more_one_year_ago_are_excluded(self):
        """Test that stock moves done today are excluded."""
        self.product.turnover_rate = 1
        self._create_quant(1)

        with freeze_time(datetime.now().date() - timedelta(367)):
            self._deliver(1)

        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == 0

    def test_stock_move_done_one_year_ago_are_included(self):
        """Test that stock moves done today are excluded."""
        self.product.turnover_rate = 1
        self._create_quant(1)

        with freeze_time(datetime.now().date() - timedelta(366)):
            self._deliver(1)

        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == 2  # 1 / ((1 + (1 - 1)) / 2)

    @data(
        (10, 4, 0.5),  # 0.5 = 4 / ((10 + (10 - 4)) / 2)
        (12, 3, 0.29),
        (1, 1, 2),
    )
    @unpack
    def test_one_quant__one_delivery(self, quant_qty, delivery_qty, expected_rate):
        self._create_quant(quant_qty)

        with freeze_time(self.yesterday):
            self._deliver(delivery_qty)

        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == expected_rate

    @data(
        (10, 2, 4, 0.44),  # 0.44 = 4 / ((10 + (10 + 2 - 4)) / 2)
        (0, 3, 3, MAX_TURNOVER_RATE),
    )
    @unpack
    def test_one_quant__one_delivery_one_receipt(
        self, quant_qty, receipt_qty, delivery_qty, expected_rate
    ):
        self._create_quant(quant_qty)

        with freeze_time(self.yesterday):
            self._receive(receipt_qty)
            self._deliver(delivery_qty)

        self.product.compute_turnover_rate()
        assert self.product.turnover_rate == expected_rate

    def test_schedule_computation(self):
        self.env.ref('stock_turnover_rate.schedule_turnover_cron').method_direct_trigger()

        job = self.env['queue.job'].search([
            ('model_name', '=', 'product.product'),
            ('method_name', '=', 'compute_turnover_rate'),
        ]).filtered(lambda j: j.record_ids == [self.product.id])

        assert len(job) == 1
