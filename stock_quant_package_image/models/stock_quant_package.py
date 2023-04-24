# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    image = fields.Binary(
        "Image",
        attachment=True,
        help="This field holds the image used for the package, about 250 x 330",
    )
