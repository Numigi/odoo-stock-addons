# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


IMPORTANT_FIELDS = [
    "property_stock_account_input_categ_id",
    "property_stock_account_output_categ_id",
    "property_stock_valuation_account_id",
    "property_stock_journal",
]


class ProductCategory(models.Model):
    _inherit = "product.category"

    def _get_product_name(self, product_id):
        return self.env["product.product"].browse(product_id).name

    def _multi_company_constraints(self, existing_move_lines):
        current_company = self.env.user.company_id.id
        if existing_move_lines:
            if current_company not in existing_move_lines.sudo().mapped(
                "move_id.company_id.id"
            ):
                return False
        return True

    def _check_category_stock_move(self):
        domain = [("product_id.categ_id", "in", self.ids)]
        existing_move_lines = self.env["stock.move.line"].search(domain)
        not_allowed = self._multi_company_constraints(existing_move_lines)
        if len(existing_move_lines) and not_allowed:
            product_lists = existing_move_lines.mapped("product_id.name")
            product_lists = (
                # select three first products found on move lines
                # if there is more than 3
                product_lists[:3]
                if len(product_lists) > 3
                else product_lists
            )
            products = "\n- ".join(product_lists)
            primary_text = _(
                """
                    You cannot modify Stock Properties Parameters when
                    related Products have existing Stock Moves.\n
                    Stock moves exist for the following products:
                    - """
            )
            raise UserError(primary_text + products)

    def write(self, vals):
        fields_changed = [f for f in IMPORTANT_FIELDS if f in vals]
        if len(fields_changed):
            self._check_category_stock_move()
        return super(ProductCategory, self).write(vals)
