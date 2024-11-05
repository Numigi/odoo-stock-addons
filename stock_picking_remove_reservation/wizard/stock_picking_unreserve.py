# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingUnreserve(models.TransientModel):
    _name = "stock.picking.unreserve"

    def action_remove_reservation(self):
        """"
        This function was inspired by the server action Correct inconsistencies for
        reservation and allows for the desynchronization of the active pickings
        """
        context = dict(self._context or {})
        if context.get('active_ids', False):
            picking_ids = self.env['stock.picking'].browse(context.get('active_ids'))
            for picking in picking_ids:
                move_line_to_recompute_ids = []
                picking.move_line_ids.with_context(bypass_reservation_update=True).sudo().write(
                    {'product_uom_qty': 0})
                move_line_to_recompute_ids += picking.move_line_ids.ids
                for line in picking.move_line_ids:
                    quants = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', line.location_id.id),
                        ('lot_id', '=', line.lot_id.id),
                        ('package_id', '=', line.package_id.id),
                        ('owner_id', '=', line.owner_id.id),
                        ('quantity', '!=', 0)])
                    for quant in quants:
                        quant.sudo().write({'reserved_quantity': 0})
                if move_line_to_recompute_ids:
                    self.env['stock.move.line'].browse(
                        move_line_to_recompute_ids).move_id._recompute_state()

        return {'type': 'ir.actions.act_window_close'}
