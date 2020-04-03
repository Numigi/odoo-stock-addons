# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data, unpack
from odoo.exceptions import ValidationError
from odoo.addons.stock_serial_single_quant.tests.common import StockMoveCase


@ddt
class TestShadowMoves(StockMoveCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_category.property_valuation = "real_time"
        cls.product_1.invoice_policy = "delivery"

        cls.value_1 = 100
        cls.value_2 = 200
        cls.value_3 = 300

        cls.product_1.standard_price = cls.value_1
        cls.product_2.standard_price = cls.value_2
        cls.product_3.standard_price = cls.value_3
        cls._make_product_output_account_reconciliable(cls.product_1)
        cls._make_product_output_account_reconciliable(cls.product_2)
        cls._make_product_output_account_reconciliable(cls.product_3)

        cls.serial_1a = cls.make_serial_number("S1-A", cls.product_1)
        cls.serial_1b = cls.make_serial_number("S1-B", cls.product_1)
        cls.serial_1c = cls.make_serial_number("S1-C", cls.product_1)
        cls.serial_1d = cls.make_serial_number("S1-D", cls.product_1)
        cls.serial_1e = cls.make_serial_number("S1-E", cls.product_1)
        cls.quant_1a = cls.make_quant(cls.location_1, cls.serial_1a)
        cls.quant_1b = cls.make_quant(cls.location_1, cls.serial_1b)
        cls.quant_1c = cls.make_quant(cls.location_1, cls.serial_1c)
        cls.quant_1d = cls.make_quant(cls.location_1, cls.serial_1d)
        cls.quant_1e = cls.make_quant(cls.location_1, cls.serial_1e)

        cls.serial_2a = cls.make_serial_number("S2-A", cls.product_2)
        cls.serial_2b = cls.make_serial_number("S2-B", cls.product_2)
        cls.serial_2c = cls.make_serial_number("S2-C", cls.product_2)
        cls.quant_2a = cls.make_quant(cls.location_1, cls.serial_2a)
        cls.quant_2b = cls.make_quant(cls.location_1, cls.serial_2b)
        cls.quant_2c = cls.make_quant(cls.location_1, cls.serial_2c)

        cls.serial_3a = cls.make_serial_number("S3-A", cls.product_3)
        cls.serial_3b = cls.make_serial_number("S3-B", cls.product_3)
        cls.quant_3a = cls.make_quant(cls.location_1, cls.serial_3a)
        cls.quant_3b = cls.make_quant(cls.location_1, cls.serial_3b)

        cls.serial_1a.add_component(cls.serial_2a)
        cls.serial_2a.add_component(cls.serial_3a)

        cls.serial_1b.add_component(cls.serial_2b)
        cls.serial_2b.add_component(cls.serial_3b)

        cls.serial_1c.add_component(cls.serial_2c)

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse_1.id,
            }
        )

        cls.line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5,
                "name": cls.product_1.display_name,
            }
        )

        cls.order.action_confirm()

        cls.deliver_serials(cls.line_1, cls.serial_1a | cls.serial_1b | cls.serial_1c)
        cls.deliver_serials(cls.line_1, cls.serial_1d)
        cls.deliver_serials(cls.line_1, cls.serial_1e)

        cls.order.action_invoice_create()

    @staticmethod
    def _make_product_output_account_reconciliable(product):
        output_account = product.product_tmpl_id._get_product_accounts()["stock_output"]
        output_account.reconcile = True

    @classmethod
    def deliver_serials(cls, sale_line, serials):
        move = sale_line.move_ids.filtered(lambda m: m.state != "done")[0]

        for serial in serials:
            cls._select_serial_on_stock_move(serial, move)

        move._action_done()

    @classmethod
    def _select_serial_on_stock_move(cls, serial, move):
        vals = move._prepare_move_line_vals()
        vals["qty_done"] = 1
        vals["lot_id"] = serial.id
        cls.env["stock.move.line"].create(vals)

    def test_get_anglo_saxon_price_unit(self):
        invoice_line = self.line_1.invoice_lines
        expected_average_price = 340  # (600 + 600 + 300 + 100 + 100) / 5
        assert invoice_line._get_anglo_saxon_price_unit() == expected_average_price

    @data((0, 0), (0, 1), (1, 1))
    @unpack
    def test_average_price__no_stock_move(self, qty_done, quantity):
        moves = self.env["stock.move"]
        result = self._compute_average_price(qty_done, quantity, moves)
        assert result == 0

    @data(
        (0, 0, 0),
        (0, 1, 600),
        (1, 1, 600),
        (1, 2, (600 + 300) / 2),
        (1, 3, (600 + 300 + 100) / 3),
        (2, 3, (300 + 100 + 100) / 3),
        (2, 4, (300 + 100 + 100) / 3),
        (3, 3, (100 + 100) / 2),
        (4, 3, 100),
        (5, 3, 0),
    )
    @unpack
    def test_average_price__one_move_shipped(
        self, qty_done, quantity, expected_average_price
    ):
        result = self._compute_average_price(qty_done, quantity, self.line_1.move_ids)
        assert result == expected_average_price

    def _compute_average_price(self, qty_done, quantity, moves):
        return self.env["product.product"]._compute_average_price(
            qty_done, quantity, moves
        )

    def test_number_of_accounts_on_parent_stock_move(self):
        account_moves = self.line_1.mapped("move_ids.account_move_ids")
        # 3 moves for P1
        # 3 for P2
        # 2 for P3
        assert len(account_moves) == 8

    def test_total_number_of_account_moves(self):
        all_account_moves = self._get_all_account_moves()
        # 3 + 3 + 2 moves for P1
        # 3 + 2 for P2
        # 2 for P3
        assert len(all_account_moves) == 15

    def test_number_of_unreconciled_account_move_lines(self):
        lines_1 = self._get_unreconciled_interim_move_lines(self.product_1)
        assert len(lines_1) == 8

        lines_2 = self._get_unreconciled_interim_move_lines(self.product_2)
        assert len(lines_2) == 0

        lines_3 = self._get_unreconciled_interim_move_lines(self.product_3)
        assert len(lines_3) == 0

    def test_value_of_interim_account(self):
        lines = self._get_unreconciled_interim_move_lines(self.product_1)

        # 1700 == 600 + 600 + 300 + 100 + 100
        assert sum(lines.mapped("debit")) - sum(lines.mapped("credit")) == 1700

    def _get_all_account_moves(self):
        products = self.product_1 | self.product_2 | self.product_3
        return self.env["account.move"].search(
            [("line_ids.product_id", "in", products.ids)]
        )

    def _get_unreconciled_interim_move_lines(self, product):
        return self.env["account.move.line"].search(
            [
                ("product_id", "=", product.id),
                ("reconciled", "=", False),
                ("account_id.reconcile", "=", True),
            ]
        )
