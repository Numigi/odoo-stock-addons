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
        quants = super()._gather(
            product_id, location_id, lot_id, package_id, owner_id, strict
        )

        # Filter quants based on the context for package reservation
        if self._context.get("reserve_full_package"):
            quants = self._filter_quants_by_package(quants, package_id)

        return quants

    def _filter_quants_by_package(self, quants, package_id):
        """Filter quants based on the package ID."""
        if package_id:
            return quants.filtered(lambda m: m.package_id == package_id)
        return quants.filtered(lambda m: not m.package_id)
