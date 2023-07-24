# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    product_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        related='product_id.categ_id',
        store=True,
    )
