# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockInventory(models.Model):

    _inherit = 'stock.inventory'

    @api.onchange('filter')
    def _onchange_filter_set_exhausted(self):
        """When selecting multiple products or a whole category, check the exausted field.

        This prevents the user from figuring out which products are exhausted.
        """
        if self.filter in ('none', 'category'):
            self.exhausted = True

    def action_start(self):
        """When the inventory is started, reset the quantities to zero."""
        res = super().action_start()
        self.action_reset_product_qty()
        return res


class StockInventoryLine(models.Model):

    _inherit = 'stock.inventory.line'

    @api.onchange(
        'product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id'
    )
    def _onchange_quantity_context(self):
        """When the product is changed, the product quantity is set to 0.

        The super method sets the product_qty equal to the theoretical_qty.

        We do not want the user to figure the theoritical quantity based on the
        new product_qty value.
        """
        super()._onchange_quantity_context()
        self.product_qty = 0
