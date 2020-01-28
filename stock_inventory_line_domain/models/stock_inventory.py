# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):

    _inherit = 'stock.inventory'

    def action_validate(self):
        for line in self.mapped('line_ids'):
            line.check_selected_product()
            line.check_selected_lot()
        return super().action_validate()


class StockInventoryLine(models.Model):

    _inherit = 'stock.inventory.line'

    def check_selected_product(self):
        if self.inventory_id.product_id:
            self._check_is_the_inventored_product()

        if self.inventory_id.category_id:
            self._check_product_belongs_to_inventory_category()

    def _check_is_the_inventored_product(self):
        if self.inventory_id.product_id != self.product_id:
            raise ValidationError(_(
                "The product {product} is different from the product "
                "selected on the inventory ({inventory_product})."
            ).format(
                product=self.product_id.display_name,
                inventory_product=self.inventory_id.product_id.display_name,
            ))

    def _check_product_belongs_to_inventory_category(self):
        product_categories = _get_category_and_all_parents(self.product_id.categ_id)
        if self.inventory_id.category_id not in product_categories:
            raise ValidationError(_(
                "The product {product} does not belong to the "
                "category selected on the inventory ({category})."
            ).format(
                product=self.product_id.display_name,
                category=self.inventory_id.category_id.display_name,
            ))

    def check_selected_lot(self):
        if self.inventory_id.lot_id:
            self._check_is_the_inventored_lot()

    def _check_is_the_inventored_lot(self):
        if self.inventory_id.lot_id != self.prod_lot_id:
            raise ValidationError(_(
                "The lot / serial number selected on the inventory ({}) "
                "must be selected on each inventory line."
            ).format(self.inventory_id.lot_id.display_name))


def _get_category_and_all_parents(category):
    return (
        _get_category_and_all_parents(category.parent_id) | category
        if category.parent_id else category
    )
