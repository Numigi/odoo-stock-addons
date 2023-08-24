# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.product"

    def _check_category_stock_move(self):
        existing_move_lines = self.env['stock.move.line'].search([
            ('product_id', 'in', self.ids)
        ])
        if existing_move_lines:
            raise UserError(
                _("You cannot modify the category of a Product with Stock Moves."))

    def write(self, vals):
        if 'categ_id' in vals:
            self._check_category_stock_move()
        return super(Product, self).write(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _check_category_stock_move(self):
        existing_move_lines = self.env['stock.move.line'].search([
            ('product_id.product_tmpl_id', 'in', self.ids)
        ])
        if existing_move_lines:
            raise UserError(
                _("You cannot modify the category of a Product with Stock Moves."))

    def write(self, vals):
        if 'categ_id' in vals:
            self._check_category_stock_move()
        return super(ProductTemplate, self).write(vals)
