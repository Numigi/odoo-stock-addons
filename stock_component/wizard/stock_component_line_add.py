# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockComponentLineAdd(models.TransientModel):

    _name = "stock.component.line.add"
    _description = "Stock Component Add Wizard"

    parent_component_id = fields.Many2one("stock.production.lot")
    product_id = fields.Many2one(
        "product.product", domain="[('tracking', '=', 'serial')]"
    )
    component_id = fields.Many2one(
        "stock.production.lot",
        domain="[('product_id', '=', product_id), ('id', '!=', parent_component_id)]",
    )

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.component_id.product_id != self.product_id:
            self.component_id = False

    def action_confirm(self):
        self.parent_component_id.add_component(self.component_id)
