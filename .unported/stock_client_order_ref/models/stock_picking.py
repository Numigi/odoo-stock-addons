# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    client_order_ref = fields.Char('Customer Reference',
                                   related='sale_id.client_order_ref',
                                   store=True
                                   )
