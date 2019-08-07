# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from .common import check_records_location_id_access, get_domain_with_location_id_filter

SCRAP_ERROR_MESSAGE = _(
    "You are not authorized to access the scrap entry {record} "
    "because it is bound to the location {location}.",
)


class StockScrap(models.Model):

    _inherit = 'stock.scrap'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_records_location_id_access(self, SCRAP_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_location_id_filter(self.env, result)
