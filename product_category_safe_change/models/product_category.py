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

    def _get_company_id_from_move(self, move_id):
        return self.env["stock.move"].search([("id", "=", move_id)]).company_id.id

    def _multi_company_constraints(self, domain, set_company=False):
        current_company = (
            self.env.user.company_id.id if not set_company else set_company.id
        )
        existing_moves = self.env["stock.move.line"].read_group(
            domain, fields=["move_id"], groupby=["move_id"]
        )

        if len(existing_moves):
            banned_company_list = [
                self._get_company_id_from_move(move["move_id"][0])
                for move in existing_moves
            ]
            if current_company not in banned_company_list:
                return False
        return True

    def _check_category_stock_move(self):
        domain = [("product_id.categ_id", "in", self.ids)]
        existing_move_lines = self.env["stock.move.line"].read_group(
            domain, fields=["product_id"], groupby=["product_id"]
        )
        not_allowed = self._multi_company_constraints(domain)
        if len(existing_move_lines) and not_allowed:
            existing_move_lines = (
                existing_move_lines[:3]
                if len(existing_move_lines) > 3
                else existing_move_lines
            )
            product_lists = [
                self._get_product_name(move["product_id"][0])
                for move in existing_move_lines
            ]
            products = "\n- ".join(product_lists)
            raise UserError(
                _(
                    """
                    You cannot modify Stock Properties Parameters when 
                    related Products have existing Stock Moves.\n
                    Stock moves exist for the following products:
                    - %s"""
                    % products
                )
            )

    def write(self, vals):
        fields_changed = [f for f in IMPORTANT_FIELDS if f in vals]
        if len(fields_changed):
            self._check_category_stock_move()
        return super(ProductCategory, self).write(vals)
