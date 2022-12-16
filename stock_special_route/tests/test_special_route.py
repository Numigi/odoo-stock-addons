# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.stock_route_optimized.tests.common import StockRouteOptimizationCase


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

    def test_search_rule_without_special_route(self):
        domain = [("id", "=", self.rule_one_step_delivery.id)]
        rule = self.procurement._search_rule(
            self.route_delivery, self.product, self.warehouse, domain
        )
        assert not rule

    def test_search_rule_with_special_route(self):
        domain = [("id", "=", self.rule_one_step_delivery.id)]
        self.product.route_ids |= self.special_route
        rule = self.procurement._search_rule(
            self.route_delivery, self.product, self.warehouse, domain
        )
        assert rule == self.rule_one_step_delivery
