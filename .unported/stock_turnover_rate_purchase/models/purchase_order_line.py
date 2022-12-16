# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    turnover_rate = fields.Float(related="product_id.turnover_rate")
    line_color = fields.Char(compute="_compute_line_color")

    def _compute_line_color(self):
        for line in self:
            minimum_rate = line.product_id.minimum_turnover_rate or 0
            target_rate = line.product_id.target_turnover_rate or 0
            effective_rate = line.product_id.turnover_rate or 0

            gte_target_rate = float_compare(effective_rate, target_rate, 2) in (0, 1)
            lte_minimum_rate = float_compare(effective_rate, minimum_rate, 2) in (-1, 0)

            if gte_target_rate:
                line.line_color = "green"

            elif lte_minimum_rate:
                line.line_color = "red"
