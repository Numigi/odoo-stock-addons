# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_launch_stock_rule(self):
        return super(SaleOrderLine, self.with_context(
            from_sale_procurement=True))._action_launch_stock_rule()
