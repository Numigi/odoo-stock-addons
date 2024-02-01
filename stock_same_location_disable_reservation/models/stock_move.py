# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        for rec in self:
            location_dest_id = (
                rec.location_dest_id.get_putaway_strategy(rec.product_id).id
                or rec.location_dest_id.id
            )
            # This will prevent to process reservation on picking
            if rec.location_id.id == location_dest_id:
                return

            super(
                StockMove, self.with_context(strict_on_location=location_dest_id)
            )._action_assign()


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
        res = super(StockQuant, self)._gather(
            product_id, location_id, lot_id, package_id, owner_id, strict
        )
        if self._context.get("strict_on_location"):
            # We do only reservation on quant that having location
            # different to location destination on picking
            res = res.filtered(
                lambda m: m.location_id.id != self._context.get("strict_on_location")
            )
        return res
