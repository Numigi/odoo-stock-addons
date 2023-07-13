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
            rec.rma_count = len(
                rec.sale_order_ids.mapped("rma_ids")) + len(rec.get_rma_from_picking())

    def get_rma_from_picking(self):
        rma = self.env["rma"]
        picking_ids = self.env["stock.move.line"].search(
            [('lot_id', '=', self.id),]).mapped("picking_id")
        for rma_line in self.env["rma"].search(
                [('state', '!=', 'draft'),]):
            if rma_line.reception_move_id.picking_id.id in picking_ids.ids:
                rma |= rma_line
        return rma

    def action_view_rma(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("rma.rma_action")
        rma = self.sale_order_ids.mapped(
            "rma_ids") | self.get_rma_from_picking()
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
