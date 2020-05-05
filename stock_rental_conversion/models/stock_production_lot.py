# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    sales_lot_id = fields.Many2one("stock.production.lot", ondelete="restrict")
    rental_lot_ids = fields.One2many("stock.production.lot", "sales_lot_id")
    sales_lot_count = fields.Integer(
        "Sales Serial Numbers Count", compute="_compute_sales_lot_count"
    )
    rental_lot_count = fields.Integer(
        "Rental Serial Numbers Count", compute="_compute_rental_lot_count"
    )

    def _compute_sales_lot_count(self):
        for lot in self:
            lot.sales_lot_count = len(lot.sales_lot_id)

    def _compute_rental_lot_count(self):
        for lot in self:
            lot.rental_lot_count = len(lot.rental_lot_ids)

    def open_sales_lot(self):
        return self.sales_lot_id.get_formview_action()

    def open_rental_lot(self):
        if len(self.rental_lot_ids) == 1:
            return self.rental_lot_ids.get_formview_action()

        action = self.env.ref(
            "stock_rental_conversion.linked_rental_lots_action"
        ).read()[0]
        action["domain"] = [("sales_lot_id", "=", self.id)]
        return action
