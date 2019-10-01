# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from itertools import groupby
from odoo import fields, models, _
from odoo.exceptions import ValidationError


def _get_origin_picking_from_line(line):
    return line.mapped('move_id.move_orig_ids.picking_id')[0]


class BackorderConfirmationWizard(models.TransientModel):

    _inherit = 'stock.backorder.confirmation'

    def _return_products_from_picking(self, origin_picking, lines):
        return_wizard_context = {
            'active_id': origin_picking.id,
        }

        return_wizard_fields = [
            'picking_id',
            'product_return_moves',
            'move_dest_exists',
            'original_location_id',
            'parent_location_id',
            'location_id',
        ]

        return_wizard_values = (
            self.env['stock.return.picking'].with_context(**return_wizard_context)
            .default_get(return_wizard_fields)
        )
        return_wizard = self.env['stock.return.picking'].create(return_wizard_values)

        for return_line in return_wizard.product_return_moves:
            related_lines = (l for l in lines if return_line.move_id in l.move_id.move_orig_ids)
            return_line.quantity = sum([
                l.product_uom_qty - (l.qty_done or 0) for l in related_lines
            ])

        new_picking_id = return_wizard.create_returns()['res_id']
        return self.env['stock.picking'].browse(new_picking_id)

    def return_products(self):
        if len(self.pick_ids) > 1:
            raise ValidationError(
                _('Products can only be returned for a single picking at a time.')
            )

        lines_to_return = self.pick_ids.move_line_ids.filtered(
            lambda l: (l.qty_done or 0) < l.product_uom_qty)

        return_pickings = self.env['stock.picking']

        for origin_picking, lines in groupby(lines_to_return, _get_origin_picking_from_line):
            return_pickings |= self._return_products_from_picking(origin_picking, list(lines))

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
            action['domain'] = [('id', 'in', return_pickings.id)]

        return action
