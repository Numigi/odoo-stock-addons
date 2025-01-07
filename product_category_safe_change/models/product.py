# Copyright 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.product"

    def _check_category_stock_move(self):
        existing_move_lines = (
            self.env["stock.move.line"].sudo().search([("product_id", "in", self.ids)])
        )
        if existing_move_lines:
            raise UserError(
                _("You cannot modify the category of a Product with Stock Moves.")
            )

    def write(self, vals):
        for rec in self:
            if rec.type != "service" and "categ_id" in vals:
                rec._check_category_stock_move()
        return super(Product, self).write(vals)
