# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockAutoAssignCronDisabled(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        if not self._context.get("stock_auto_assign_disable"):
            super()._action_assign()
