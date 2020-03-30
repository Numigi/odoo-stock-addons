# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockComponentLine(models.Model):

    _name = 'stock.component.line'
    _description = 'Component Line on Serial Number'

    sequence = fields.Integer()

    parent_component_id = fields.Many2one(
        "stock.production.lot",
        "Serial Number",
        ondelete="restrict",
        index=True,
    )

    product_id = fields.Many2one(
        related="component_id.product_id",
    )

    component_id = fields.Many2one(
        "stock.production.lot",
        "Component",
        ondelete="restrict",
        index=True,
    )
