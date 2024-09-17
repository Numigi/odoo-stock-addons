# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(self, need, available_quantity, location_id,
                                  lot_id=None, package_id=None, owner_id=None,
                                  strict=True):
        if self.picking_code not in ['incoming', 'outgoing']:
            self = self.with_context(dest_location=self.location_dest_id)
        taken_quantity = super(StockMove, self)._update_reserved_quantity(
            need, available_quantity, location_id, lot_id, package_id,
            owner_id, strict
        )
        return taken_quantity


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
        dest_location = self._context.get("dest_location")
        if dest_location:
            # We do only reservation on quant that having location
            # different to location destination on picking
            quants = quants.filtered(lambda q: q.location_id != dest_location)
        return quants
