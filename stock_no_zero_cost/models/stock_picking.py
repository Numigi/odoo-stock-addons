# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _pre_action_done_hook(self):
        print("""
        Intercept the validation flow to check for zero cost moves.
        Shows a wizard for authorized users, blocks unauthorized users.
        """)
        # If the context tells us to skip (because the wizard was confirmed), we bypass
        if not self.env.context.get('skip_zero_cost_check'):
            pickings_to_warn = self.env['stock.picking']
            moves_to_warn = self.env['stock.move']

            for picking in self:
                for move in picking.move_lines:
                    # Filter: Only stockable products, incoming/internal, and not yet done/cancelled
                    if move.state not in ('done', 'cancel') and move.product_id.type == 'product':
                        if move.location_dest_id.usage == 'internal':
                            currency = move.company_id.currency_id or self.env.company.currency_id
                            cost = move.price_unit if move._is_in() else move.product_id.standard_price

                            if float_is_zero(cost, precision_rounding=currency.rounding):
                                pickings_to_warn |= picking
                                moves_to_warn |= move

            if pickings_to_warn:
                # Security Check
                if not self.env.user.has_group('stock_no_zero_cost.group_allow_zero_cost_move'):
                    raise UserError(_(
                        "You are not allowed to validate an Incoming or Internal stock move with a zero cost. "
                        "Please contact your stock manager to authorize this transfer."
                    ))

                # Show the Wizard to the authorized manager
                return {
                    'name': _('Zero Cost Valuation Warning'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_picking_id': pickings_to_warn[0].id,
                        'default_move_ids': [(6, 0, moves_to_warn.ids)]
                    }
                }

        # Proceed with standard Odoo hooks (Backorder wizards, etc.)
        return super(StockPicking, self)._pre_action_done_hook()