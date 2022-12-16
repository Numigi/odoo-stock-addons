# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        self_with_context = self.with_context(stock_auto_assign_disable=True)
        super(ProcurementGroup, self_with_context)._run_scheduler_tasks(
            use_new_cursor=use_new_cursor, company_id=company_id
        )
