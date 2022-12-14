# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    usual_location_ids = fields.Many2many(
        "stock.location",
        "product_template_usual_location_rel",
        "product_template_id",
        "location_id",
        "Usual Location",
        domain="[('usage', '=', 'internal')]",
    )
