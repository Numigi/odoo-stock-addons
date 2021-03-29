# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    use_partner_signature = fields.Boolean("Partner Signature")
