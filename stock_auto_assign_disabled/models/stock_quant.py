# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        if self._context.get("disable_reservation"):
            return self.env["stock.quant"]
        else:
            return super(StockQuant, self)._gather(
                product_id, location_id, lot_id, package_id, owner_id, strict)
