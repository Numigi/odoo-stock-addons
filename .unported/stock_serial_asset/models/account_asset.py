# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAsset(models.Model):

    _inherit = "account.asset"

    serial_number_id = fields.Many2one(
        "stock.production.lot", "Serial Number", copy=False
    )
