# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import StockRouteOptimizationCase


class TestSpecialRoute(StockRouteOptimizationCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.special_route = cls.env["stock.location.route"].create(
            {"name": "Special Route"}
        )
        cls.rule_one_step_delivery.special_route_id = cls.special_route

    def test_product_not_matching(self):
        rule = self.procurement._get_rule(
            self.product, self.customer_location, self.values
        )
        assert not rule

    def test_product_matching(self):
        self.product.route_ids |= self.special_route
        rule = self.procurement._get_rule(
            self.product, self.customer_location, self.values
        )
        assert rule == self.rule_one_step_delivery

    def test_product_category_matching(self):
        self.product.categ_id.route_ids |= self.special_route
        rule = self.procurement._get_rule(
            self.product, self.customer_location, self.values
        )
        assert rule == self.rule_one_step_delivery
