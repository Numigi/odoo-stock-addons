# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def get_total_unit_price(self):
        return self.move_id.price_unit + sum(
            l.get_total_unit_price() for l in self.child_ids
        )
