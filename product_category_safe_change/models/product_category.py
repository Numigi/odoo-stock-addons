# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
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

    def _check_category_stock_move(self):
        domain = [
            ("product_id.categ_id", "in", self.ids),
            ("company_id", "=", self.env.company.id)
        ]
        existing_move_lines = self.env["stock.move.line"].sudo().search(domain)
        if len(existing_move_lines):
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
