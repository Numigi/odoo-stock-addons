# Copyright 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.constrains(
        "property_stock_account_input_categ_id",
        "property_stock_account_output_categ_id",
        "property_stock_valuation_account_id",
        "property_stock_journal",
    )
    def _check_category_stock_move(self):
        for category in self:
            domain = [
                ("product_id.categ_id", "=", category.id),
                ("company_id", "=", self.env.company.id),
            ]
            existing_move_lines = self.env["stock.move.line"].sudo().search(domain)

            if existing_move_lines:
                # Select only three first products found on move lines
                # if there is more than 3
                product_lists = existing_move_lines.mapped("product_id.name")
                product_lists = (
                    product_lists[:3] if len(product_lists) > 3 else product_lists
                )
                products = "\n- ".join(product_lists)

                message = _(
                    """
                    You cannot modify Stock Properties Parameters when
                    related Products have existing Stock Moves.\n
                    Stock moves exist for the following products:
                    - """
                )
                raise UserError(message + products)
