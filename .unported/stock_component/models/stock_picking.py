# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.move.line"

    has_components = fields.Boolean(
        compute="_compute_has_components",
    )

    @api.multi
    def display_components(self):
        return self.lot_id.get_formview_action()

    @api.multi
    def _compute_has_components(self):
        for line in self:
            line.has_components = bool(line.lot_id.component_ids)

