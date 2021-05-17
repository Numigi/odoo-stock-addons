# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockRule(models.Model):

    _inherit = "stock.rule"

    special_route_id = fields.Many2one(
        "stock.location.route",
        ondelete="restrict",
    )

    def _matches_product(self, product):
        res = super()._matches_product(product)
        return res and (
            not self.special_route_id or self._product_matches_special_route(product)
        )

    def _product_matches_special_route(self, product):
        return self.special_route_id in product._get_stock_routes()
