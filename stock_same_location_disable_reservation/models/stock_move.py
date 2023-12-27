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
            if rec.location_id.id == location_dest_id:
                return
        return super()._action_assign()
