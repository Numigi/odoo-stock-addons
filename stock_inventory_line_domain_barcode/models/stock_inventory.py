# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.exceptions import ValidationError


class StockInventory(models.Model):

    _inherit = 'stock.inventory'

    def on_barcode_scanned(self, barcode):
        lines_before = self.line_ids
        super().on_barcode_scanned(barcode)
        lines_after = self.line_ids
        new_lines = lines_after - lines_before
        for line in new_lines:
            line.check_selected_product()
