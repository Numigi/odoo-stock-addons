# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _get_stock_routes(self):
        return self.route_ids | self.categ_id.total_route_ids
