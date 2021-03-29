# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    mandatory_delivery_order_signature = fields.Boolean()
