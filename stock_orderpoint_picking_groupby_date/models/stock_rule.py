# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_procurement_group_data(self, date):
        name = self.env["ir.sequence"].next_by_code("procurement.group") or False
        if not name:
            raise UserError(_("No sequence defined for procurement group."))
        return {
            "name": name,
            "scheduled_date": date,
        }

    def _get_procurement_group(self, date):
        ProcObject = self.env["procurement.group"]
        if date:
            group_id = ProcObject.search(
                [
                    ("partner_id", "=", self.partner_address_id.id),
                    ("scheduled_date", "=", date),
                ],
                order="scheduled_date desc",
                limit=1,
            )
            if group_id:
                return group_id
        group_data = self._prepare_procurement_group_data(date)
        return self.env["procurement.group"].create(group_data)

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        group = self._get_procurement_group(move_to_copy.date)
        new_move_vals["group_id"] = group.id
        return new_move_vals
