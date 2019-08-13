# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND

PURCHASE_ORDER_ERROR_MESSAGE = _(
    "You are not authorized to access the purchase order {order} "
    "because it is related to the warehouse {warehouse}."
)

PURCHASE_LINE_ERROR_MESSAGE = _(
    "You are not authorized to access the purchase order line {line} "
    "because it is related to the warehouse {warehouse}."
)


def _get_authorized_picking_types(user: models.Model):
    """Get the authorized stock picking types for the given user."""
    return user.env['stock.picking.type'].search([
        '|',
        ('warehouse_id', 'in', user.warehouse_ids.ids),
        ('warehouse_id', '=', False),
    ])


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def check_extended_security_all(self):
        super().check_extended_security_all()

        for po in self:
            warehouse = po.picking_type_id.warehouse_id
            if warehouse and not self.env.user.has_warehouse_access(warehouse):
                raise AccessError(
                    _(PURCHASE_ORDER_ERROR_MESSAGE)
                    .format(order=po.display_name, warehouse=warehouse.display_name)
                )

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        user = self.env.user
        if not user.all_warehouses:
            authorized_picking_types = _get_authorized_picking_types(user)
            result = AND((result, [('picking_type_id', 'in', authorized_picking_types.ids)]))

        return result


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    def check_extended_security_all(self):
        super().check_extended_security_all()

        for line in self:
            warehouse = line.order_id.picking_type_id.warehouse_id
            if warehouse and not self.env.user.has_warehouse_access(warehouse):
                raise AccessError(
                    _(PURCHASE_LINE_ERROR_MESSAGE)
                    .format(line=line.display_name, warehouse=warehouse.display_name)
                )

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        user = self.env.user
        if not user.all_warehouses:
            authorized_picking_types = _get_authorized_picking_types(user)
            result = AND((result, [
                ('order_id.picking_type_id', 'in', authorized_picking_types.ids)
            ]))

        return result
