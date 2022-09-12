# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.purchase_stock.models.stock import Orderpoint


def _quantity_in_progress(self):
    res = super(Orderpoint, self)._quantity_in_progress()
    for rec in self:
        domain = [
            ('state', 'in', ('draft', 'sent', 'to approve')),
            ('product_id', '=', rec.product_id.id),
            ('order_id.picking_type_id.warehouse_id', '=', rec.warehouse_id.id)
            ]
        for poline in self.env['purchase.order.line'].search(domain):
            res[rec.id] += poline.product_uom._compute_quantity(
                poline.product_qty, rec.product_uom, round=False)
    return res


Orderpoint._quantity_in_progress = _quantity_in_progress
