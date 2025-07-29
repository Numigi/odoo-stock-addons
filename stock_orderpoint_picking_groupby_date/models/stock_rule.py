# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
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
            "from_orderpoint": True,
            "scheduled_date": date,
        }

    def _get_procurement_group(self, date, orderpoint_id):
        ProcObject = self.env["procurement.group"]
        if date and orderpoint_id:
            group_id = ProcObject.search(
                [
                    ("from_orderpoint", "=", True),
                    ("scheduled_date", "=", date),
                ],
                order="scheduled_date desc",
                limit=1,
            )
            if group_id:
                return group_id
        group_data = self._prepare_procurement_group_data(date)
        return self.env["procurement.group"].create(group_data)
