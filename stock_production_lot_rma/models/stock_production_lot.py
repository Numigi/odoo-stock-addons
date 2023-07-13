# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    rma_count = fields.Integer(
        string="RMA count",
        compute="_compute_rma_count",
    )

    def _compute_rma_count(self):
        for rec in self:
            rec.rma_count = len(rec.get_rma())

    def get_rma(self):
        rma = self.env['rma']
        # RMAs that were created from the delivery move
        rma_ids = self.env["stock.move.line"].search(
            [('lot_id', '=', self.id)]).mapped("move_id.rma_ids")
        # RMAs linked to the incoming movement from client
        rma_receiver_ids = self.env["stock.move.line"].search(
            [('lot_id', '=', self.id)]).mapped("move_id.rma_receiver_ids")
        # RMA that create the delivery movement to the customer
        rma_id = self.env["stock.move.line"].search(
            [('lot_id', '=', self.id)]).mapped("move_id.rma_id")
        rma |= rma_ids + rma_receiver_ids + rma_id
        return rma

    def action_view_rma(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("rma.rma_action")
        rma = self.get_rma()
        if len(rma) == 1:
            action.update(
                res_id=rma.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        else:
            action["domain"] = [("id", "in", rma.ids)]
        return action
