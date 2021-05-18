# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import StockRouteOptimizationCase


class TestProcurementGroup(StockRouteOptimizationCase):
    def test_basic_case(self):
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert rule == self.rule_one_step_delivery

    def test_child_location(self):
        rule = self.procurement._get_rule(self.product, self.child_customer_location, self.values)
        assert rule == self.rule_one_step_delivery

    def test_location_not_matching(self):
        self.rule_one_step_delivery.location_id = self.child_customer_location
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert not rule

    def test_make_to_order(self):
        self.values["route_ids"] = self.env.ref("stock.route_warehouse0_mto")
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert rule == self.warehouse.mto_pull_id

    def test_make_to_order_different_warehouse(self):
        self.values["warehouse_id"] = self.warehouse_2
        self.values["route_ids"] = self.env.ref("stock.route_warehouse0_mto")
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert rule == self.warehouse_2.mto_pull_id

    def test_company_not_matching(self):
        self.values["company_id"] = self.company_2
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert not rule

    def test_warehouse_not_given(self):
        self.values["warehouse_id"] = False
        self.values["route_ids"] = self.warehouse.delivery_route_id
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert rule == self.rule_one_step_delivery

    def test_product_routes(self):
        route = self.warehouse.delivery_route_id
        self.warehouse.route_ids -= route
        self.product.categ_id.route_ids = False
        self.product.route_ids = route
        rule = self.procurement._get_rule(self.product, self.customer_location, self.values)
        assert rule == self.rule_one_step_delivery
