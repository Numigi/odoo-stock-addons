# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def is_in_the_same_warehouse_than(self, location):
        return self.get_warehouse() == location.get_warehouse()
