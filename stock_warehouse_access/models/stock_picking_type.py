# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    def check_extended_security_all(self):
        super().check_extended_security_all()

        for picking_type in self:
            warehouse = picking_type.warehouse_id
            if warehouse and not self.env.user.has_warehouse_access(warehouse):
                raise AccessError(_(
                    "You are not authorized to access the stock picking type {type_} "
                    "because it is related to the warehouse {warehouse}."
                ).format(type_=picking_type.display_name, warehouse=warehouse.display_name))

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        user = self.env.user

        if not user.all_warehouses:
            result = AND((result, [
                '|',
                ('warehouse_id', 'in', user.warehouse_ids.ids),
                ('warehouse_id', '=', False),
            ]))

        return result
