# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    rental_conversion_account_id = fields.Many2one(
        "account.account", company_dependent=True, domain=[("deprecated", "=", False)]
    )
