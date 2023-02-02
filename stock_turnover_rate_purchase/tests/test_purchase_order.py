# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from datetime import datetime
from ddt import data, ddt, unpack
from odoo.tests import common
from odoo.exceptions import ValidationError


@ddt
class TestPurchaseOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = cls.env["product.category"].create(
            {"name": "Category", "minimum_turnover_rate": 2, "target_turnover_rate": 3}
        )

        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "type": "product", "categ_id": cls.category.id}
        )

        cls.supplier = cls.env["res.partner"].create(
            {"name": "Supplier", "supplier_rank": 1}
        )

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 2,
                            "product_uom": cls.product.uom_po_id.id,
                            "price_unit": 10,
                            "date_planned": datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.line = cls.po.order_line

    @data(False, 0, 1.99, 2.00)
    def test_po_line_red(self, turnover_rate):
        self.product.turnover_rate = turnover_rate
        assert self.line.line_color == "red"

    @data(2.01, 2.99)
    def test_po_line_uncolored(self, turnover_rate):
        self.product.turnover_rate = turnover_rate
        assert not self.line.line_color

    @data(3, 3.01)
    def test_po_line_green(self, turnover_rate):
        self.product.turnover_rate = turnover_rate
        assert self.line.line_color == "green"

    def test_empty_minimum_turnover_rate_evaluated_as_0(self):
        self.category.minimum_turnover_rate = None
        self.product.turnover_rate = 2.5
        assert not self.line.line_color

    @data(False, 0, 1.0)
    def test_if_empty_target_turnover_rate__line_is_green(self, rate):
        self.category.write(
            {"minimum_turnover_rate": None, "target_turnover_rate": None}
        )
        self.product.turnover_rate = rate
        assert self.line.line_color == "green"

    def test_if_minimum_rate_greater_than_target__raise_error(self):
        with pytest.raises(ValidationError):
            self.category.minimum_turnover_rate = 3.01

    @data((False, "red"), (1.99, "red"), (2, "green"), (2.01, "green"))
    @unpack
    def test_if_minimum_rate_greater_equal_to_target__line_never_uncolored(
        self, rate, color
    ):
        self.category.target_turnover_rate = 2
        self.product.turnover_rate = rate
        assert self.line.line_color == color
