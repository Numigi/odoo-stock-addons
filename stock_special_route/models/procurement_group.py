# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.osv.expression import AND


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    @api.model
    def _search_rule(self, route_ids, product_id, warehouse_id, domain):
        """Filter rules per special route.

        Override this method to support cases where _search_rule is called directly
        instead of _get_rule.

        This happens when stocks are pushed.

        In the case of a procurement, the module stock_route_optimized allows
        to filter in a more performant way.
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
