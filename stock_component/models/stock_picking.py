# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.move.line"

    has_components = fields.Boolean(
        compute="_check_has_components",
        default=False,
    )

    @api.multi
    def display_components(self):
        return self.lot_id.get_formview_action()

    @api.multi
    def _check_has_components(self):
        for line in self:
            if line.lot_id.component_ids:
                line.has_components = True

