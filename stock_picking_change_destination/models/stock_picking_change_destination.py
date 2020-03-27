# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, api


class StockPickingChangeDestLocation(models.TransientModel):
    _name = "stock.picking.change.destination"

    location_dest_id = fields.Many2one(
        "stock.location", "Destination Location Zone", required=True
    )

    picking_id = fields.Many2one(
        "stock.picking", "Picking", required=True, ondelete="cascade"
    )

    @api.multi
    def set_location_destination(self):
        if self.location_dest_id and self.picking_id:
            self.picking_id.set_location_destination(self.location_dest_id)
