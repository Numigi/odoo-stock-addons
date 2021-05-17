# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.osv.expression import AND


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        return next(
            (
                r
                for r in self._iter_matching_rules(product_id, location_id, values)
                if r._matches_product(product_id)
            ),
            None,
        )

    def _iter_matching_rules(self, product, base_location, values):
        for data in self._iter_matching_rules_data(product, base_location, values):
            yield self.env["stock.rule"].browse(data["id"])

    def _iter_matching_rules_data(self, product, base_location, values):
        rules = self.env["stock.rule"]._get_procurement_rules_data()
        rules = _filter_rules_matching_company(rules, values)
        rules = _filter_rules_matching_warehouse(rules, values)

        routes = values.get("route_ids")
        warehouse = values.get("warehouse_id")

        for location in _iter_locations(base_location):
            yield from _iter_rules_matching_location(
                rules, routes, product, warehouse, location
            )

    @api.model
    def _search_rule(self, route_ids, product_id, warehouse_id, domain):
        """Filter rules per special route.

        Override this method to support cases where _search_rule is called directly
        instead of _get_rule.

        This happens when stocks are pushed.
        """
        domain = AND(
            [
                domain,
                [
                    "|",
                    ("special_route_id", "=", False),
                    ("special_route_id", "in", product_id._get_stock_routes().ids),
                ],
            ]
        )
        return super()._search_rule(route_ids, product_id, warehouse_id, domain)


def _filter_rules_matching_location(rules, location):
    return [r for r in rules if r["location_id"] == location.id]


def _filter_rules_matching_company(rules, values):
    company = values.get("company_id")
    if company:
        return [
            r for r in rules if not r["company_id"] or r["company_id"] in company.ids
        ]
    return rules


def _filter_rules_matching_warehouse(rules, values):
    warehouse = values.get("warehouse_id")
    if warehouse:
        return [
            r
            for r in rules
            if not r["warehouse_id"] or r["warehouse_id"] in warehouse.ids
        ]
    return rules


def _iter_rules_matching_location(rules, routes, product, warehouse, location):
    rules = _filter_rules_matching_location(rules, location)

    yield from _iter_rules_matching_routes(rules, routes)
    yield from _iter_rules_matching_product(rules, product)

    if warehouse:
        yield from _iter_rules_matching_warehouse(rules, warehouse)


def _iter_rules_matching_product(rules, product):
    yield from _iter_rules_matching_routes(rules, product._get_stock_routes())


def _iter_rules_matching_warehouse(rules, warehouse):
    yield from _iter_rules_matching_routes(rules, warehouse.route_ids)


def _iter_rules_matching_routes(rules, routes):
    if not routes:
        return

    for rule in rules:
        if rule["route_id"] in routes.ids:
            yield rule


def _iter_locations(location):
    while location:
        yield location
        location = location.location_id
