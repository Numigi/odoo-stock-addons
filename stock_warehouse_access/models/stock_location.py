# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND


class Location(models.Model):

    _inherit = 'stock.location'

    def check_extended_security_all(self):
        super().check_extended_security_all()

        for location in self:
            warehouse = location.get_warehouse()
            if warehouse and not self.env.user.has_warehouse_access(warehouse):
                raise AccessError(_(
                    "You are not authorized to access the stock location {}."
                ).format(location.display_name))

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        user = self.env.user

        if not user.all_warehouses:
            unauthorized_location_ids = user.get_unauthorized_location_ids()
            result = AND((result, [('id', 'not in', unauthorized_location_ids)]))

        return result
