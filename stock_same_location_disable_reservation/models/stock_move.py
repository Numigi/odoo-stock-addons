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

            has_child_parent_relation = rec._has_location_parent_relation(
                rec.location_id.id, location_dest_id
            )
            if rec.location_id.id == location_dest_id or has_child_parent_relation:
                return
        return super()._action_assign()

    def _has_location_parent_relation(
        self, source_location_id, destination_location_id
    ):
        has_relation = False
        locations = (
            self.env["stock.location"]
            .search([("id", "parent_of", [destination_location_id])])
            .ids
        )
        if source_location_id in locations:
            has_relation = True
        return has_relation
