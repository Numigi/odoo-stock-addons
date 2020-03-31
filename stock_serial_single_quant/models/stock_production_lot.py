# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    def get_current_location(self):
        quants = self.get_positive_quants()
        return quants.mapped("location_id")

    def get_current_package(self):
        quants = self.get_positive_quants()
        return quants.mapped("package_id")

    def get_current_owner(self):
        quants = self.get_positive_quants()
        return quants.mapped("owner_id")

    def get_positive_quants(self):
        return self.mapped("quant_ids").filtered(lambda q: q.quantity > 0)
