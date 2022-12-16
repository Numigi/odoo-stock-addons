# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.osv.expression import AND


class Product(models.Model):

    _inherit = 'product.product'

    def _search(self, args, *args_, **kwargs):
        args = _add_product_domain_if_required(args, self._context)
        args = _add_product_category_domain_if_required(args, self._context)
        args = _add_product_lot_domain_if_required(args, self.env, self._context)
        return super()._search(args, *args_, **kwargs)


def _add_product_domain_if_required(domain, context):
    product_id = context.get('stock_inventory_product_filter')
    if product_id:
        domain = AND((domain or [], [('id', '=', product_id)]))
    return domain


def _add_product_category_domain_if_required(domain, context):
    category_id = context.get('stock_inventory_product_category_filter')
    if category_id:
        domain = AND((domain or [], [('categ_id', 'child_of', category_id)]))
    return domain


def _add_product_lot_domain_if_required(domain, env, context):
    lot_id = context.get('stock_inventory_product_lot_filter')
    if lot_id:
        lot = env['stock.production.lot'].browse(lot_id)
        domain = AND((domain or [], [('id', '=', lot.product_id.id)]))
    return domain
