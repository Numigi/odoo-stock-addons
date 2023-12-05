# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        location_dest_id = (
            self.location_dest_id.get_putaway_strategy(self.product_id).id
            or self.location_dest_id.id
        )
        if (
            self.env.context.get("disable_same_location_reservation")
            and self.location_id.id == location_dest_id
        ):
            return
        return super()._action_assign()
