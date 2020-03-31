# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockComponentLineRemove(models.TransientModel):

    _name = "stock.component.line.remove"
    _description = "Stock Component Remove Wizard"

    parent_component_id = fields.Many2one("stock.production.lot")
    component_ids = fields.Many2many(
        "stock.production.lot",
        "stock_component_line_remove_rel",
        "wizard_id",
        "component_id",
        domain="[('parent_component_id', '=', parent_component_id)]",
    )

    def action_confirm(self):
        for component in self.component_ids:
            self.parent_component_id.remove_component(component)
