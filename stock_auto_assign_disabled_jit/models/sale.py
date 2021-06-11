# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_launch_stock_rule(self):
        self_with_context = self.with_context(stock_auto_assign_disable=True)
        super(SaleOrderLine, self_with_context)._action_launch_stock_rule()