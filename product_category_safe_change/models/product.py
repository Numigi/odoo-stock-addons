# Copyright 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.product"

    @api.constrains("categ_id")
    def _check_category_stock_move(self):
        for product in self:
            if product.type != "service":
                existing_move_lines = (
                    self.env["stock.move.line"]
                    .sudo()
                    .search([("product_id", "=", product.id)])
                )
                if existing_move_lines:
                    raise UserError(
                        _(
                            "You cannot modify the category of a Product with Stock Moves."
                        )
                    )
