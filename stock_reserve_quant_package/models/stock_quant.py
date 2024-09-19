# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
        quants = super(StockQuant, self)._gather(
                product_id, location_id, lot_id, package_id, owner_id, strict
        )
        if package_id and not strict:
            quants = quants.filtered(
                lambda m: m.package_id == package_id or False
            )
        return quants
