# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    rma_count = fields.Integer(
        string="RMA count",
        compute="_compute_rma_count",
    )

    def _compute_rma_count(self):
        for rec in self:
            rec.rma_count = len(
                rec.sale_order_ids.picking_ids.move_lines.mapped("rma_ids"))

    def action_view_rma(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("rma.rma_action")
        rma = self.sale_order_ids.picking_ids.move_lines.mapped("rma_ids")
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
