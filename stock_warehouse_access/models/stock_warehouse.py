# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND


class Warehouse(models.Model):

    _inherit = 'stock.warehouse'

    def check_extended_security_all(self):
        super().check_extended_security_all()

        for warehouse in self:
            if not self.env.user.has_warehouse_access(warehouse):
                raise AccessError(_(
                    "You are not authorized to access the warehouse {}."
                ).format(warehouse.display_name))

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        user = self.env.user
        if not user.all_warehouses:
            result = AND((result, [('id', 'in', user.warehouse_ids.ids)]))

        return result
