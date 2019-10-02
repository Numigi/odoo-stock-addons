# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from itertools import groupby
from odoo import fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def _get_origin_picking_from_move(move: 'stock.move') -> 'stock.picking':
    """Get the origin picking from a single stock move.

    If more than one origin picking is related to the move,
    take the first one in create order.
    """
    return move.mapped('move_orig_ids.picking_id').sorted(key=lambda p: p.id)[0]


def _link_origin_and_return_pickings(
    origin_picking: 'stock.picking',
    return_picking: 'stock.picking',
):
    return_picking.message_post_with_view(
        'mail.message_origin_link',
        values={'self': return_picking, 'origin': origin_picking},
        subtype_id=origin_picking.env.ref('mail.mt_note').id
    )


def _prepare_return_move_values(
    move_to_return: 'stock.move', return_picking: 'stock.picking', quantity: float
) -> dict:
    return {
        'product_id': move_to_return.product_id.id,
        'product_uom_qty': quantity,
        'product_uom': move_to_return.product_uom.id,
        'picking_id': return_picking.id,
        'state': 'draft',
        'location_id': move_to_return.location_dest_id.id,
        'location_dest_id': move_to_return.location_id.id,
        'picking_type_id': return_picking.picking_type_id.id,
        'warehouse_id': return_picking.picking_type_id.warehouse_id.id,
        'procure_method': 'make_to_stock',
        'origin_returned_move_id': move_to_return.id,
    }


def _prepare_return_picking_values(origin_picking: 'stock.picking') -> dict:
    return_picking_type = (
        origin_picking.picking_type_id.return_picking_type_id or
        origin_picking.picking_type_id
    )
    return {
        'move_lines': [],
        'picking_type_id': return_picking_type.id,
        'state': 'draft',
        'origin': _("Return of %s") % origin_picking.name,
        'location_id': origin_picking.location_dest_id.id,
        'location_dest_id': origin_picking.location_id.id,
    }


def _return_single_stock_move(return_picking: 'stock.picking', move: 'stock.move'):
    qty_to_return = move.product_uom_qty
    for move_to_return in move.move_orig_ids:
        if qty_to_return:
            returned_qty = min(move_to_return.product_uom_qty, qty_to_return)
            vals = _prepare_return_move_values(move_to_return, return_picking, returned_qty)
            move_to_return.copy(vals)
            qty_to_return -= returned_qty


def _return_products_from_origin_picking(origin_picking: 'stock.picking', moves: 'stock.move'):
    origin_picking_vals = _prepare_return_picking_values(origin_picking)
    return_picking = origin_picking.copy(origin_picking_vals)
    _link_origin_and_return_pickings(origin_picking, return_picking)

    for move in moves:
        _return_single_stock_move(return_picking, move)

    return_picking.action_confirm()
    return_picking.action_assign()
    return return_picking


class BackorderConfirmationWizard(models.TransientModel):

    _inherit = 'stock.backorder.confirmation'

    show_return_products_button = fields.Boolean(compute='_compute_buttons_visibility')
    show_no_backorder_button = fields.Boolean(compute='_compute_buttons_visibility')

    def _compute_buttons_visibility(self):
        for wizard in self:
            pick_types = wizard.pick_ids.mapped('picking_type_id')
            wizard.show_return_products_button = all(
                p.enable_previous_step_return for p in pick_types
            )
            wizard.show_no_backorder_button = all(
                p.enable_no_backorder for p in pick_types
            )

    def _get_returned_pickings_action(self, return_pickings):
        action = {
            'name': _('Returned Pickings'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': dict(self.env.context),
        }

        if len(return_pickings) == 1:
            action['view_type'] = 'form'
            action['res_id'] = return_pickings.id
        else:
            action['view_type'] = 'tree'
            action['domain'] = [('id', 'in', return_pickings.ids)]

        return action

    def button_return_products(self):
        self._process()

        backorders = self.env['stock.picking'].search([('backorder_id', 'in', self.pick_ids.ids)])
        backorders.do_unreserve()

        moves_to_return = backorders.mapped('move_lines')
        return_pickings = self.env['stock.picking']

        for origin_picking, moves in groupby(moves_to_return, _get_origin_picking_from_move):
            return_pickings |= _return_products_from_origin_picking(origin_picking, list(moves))

        return self._get_returned_pickings_action(return_pickings)
