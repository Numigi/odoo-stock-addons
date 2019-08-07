# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from .common import check_stock_move_access, get_domain_with_stock_move_filter

MOVE_ERROR_MESSAGE = _(
    "You are not authorized to access the stock move {record} "
    "because it is bound to the location {location}.",
)

MOVE_LINE_ERROR_MESSAGE = _(
    "You are not authorized to access the stock move line {record} "
    "because it is bound to the location {location}.",
)

PICKING_ERROR_MESSAGE = _(
    "You are not authorized to access the stock picking {record} "
    "because it is bound to the location {location}.",
)


class StockMove(models.Model):

    _inherit = 'stock.move'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_stock_move_access(self, MOVE_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_stock_move_filter(self.env, result)


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_stock_move_access(self, MOVE_LINE_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_stock_move_filter(self.env, result)


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def check_extended_security_all(self):
        super().check_extended_security_all()
        check_stock_move_access(self, PICKING_ERROR_MESSAGE, self._context)

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()
        return get_domain_with_stock_move_filter(self.env, result)
