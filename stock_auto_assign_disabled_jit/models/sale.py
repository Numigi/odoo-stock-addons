# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        self_with_context = self.with_context(stock_auto_assign_disable=True)
        res = super(SaleOrderLine, self_with_context)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
        return res
