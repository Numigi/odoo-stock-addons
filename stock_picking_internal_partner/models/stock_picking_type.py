# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    warehouse_as_partner = fields.Boolean(
        string='Set warehouse as partner of transfer',
    )

    @api.onchange('code')
    def onchange_picking_code(self):
        super(StockPickingType, self).onchange_picking_code()
        if self.code == 'internal':
            self.warehouse_as_partner = True
