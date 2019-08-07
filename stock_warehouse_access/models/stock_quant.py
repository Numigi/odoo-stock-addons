# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from .common import check_records_location_id_access, get_domain_with_location_id_filter

QUANT_ERROR_MESSAGE = _(
    "You are not authorized to access the stock quant {record} "
    "because it is bound to the location {location}.",
)

PACKAGE_ERROR_MESSAGE = _(
    "You are not authorized to access the package {record} "
    "because it is bound to the location {location}.",
)


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_records_location_id_access(self, QUANT_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_location_id_filter(self.env, result)


class StockQuantPackage(models.Model):

    _inherit = 'stock.quant.package'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_records_location_id_access(self, PACKAGE_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_location_id_filter(self.env, result)
