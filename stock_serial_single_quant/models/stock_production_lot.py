# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    is_serial = fields.Boolean(
        "Is Serial Number", compute="_compute_is_serial", compute_sudo=True, store=True
    )

    location_id = fields.Many2one(
        "stock.location",
        compute="_compute_location_id",
        compute_sudo=True,
        store=True,
        index=True,
    )

    @api.depends("quant_ids", "quant_ids.quantity")
    def _compute_location_id(self):
        for lot in self:
            lot.location_id = lot.get_current_location()[:1]

    @api.depends("product_id", "product_id.tracking")
    def _compute_is_serial(self):
        for lot in self:
            lot.is_serial = lot.product_id.tracking == "serial"

    def get_current_location(self):
        quants = self.get_positive_quants()
        return quants.mapped("location_id")

    def get_current_package(self):
        quants = self.get_positive_quants()
        return quants.mapped("package_id")

    def get_current_owner(self):
        quants = self.get_positive_quants()
        return quants.mapped("owner_id")

    def get_positive_quants(self):
        return self.mapped("quant_ids").filtered(lambda q: q.quantity > 0)
