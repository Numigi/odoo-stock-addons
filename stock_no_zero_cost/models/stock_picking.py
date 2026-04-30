# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _pre_action_done_hook(self):
        # --- BYPASS POUR LES TESTS STANDARDS ODOO ---
        if tools.config['test_enable'] and not self.env.context.get('force_zero_cost_check'):
            return super(StockPicking, self)._pre_action_done_hook()
        # If the context tells us to skip (because the wizard was confirmed), we bypass
        if not self.env.context.get('skip_zero_cost_check'):
            pickings_to_warn = self.env['stock.picking']
            moves_to_warn = self.env['stock.move']

            # 1. Initialisation de la liste pour stocker les noms des articles
            products_with_zero_cost = []

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
                                # 2. Ajout du nom de l'article à la liste
                                products_with_zero_cost.append(move.product_id.display_name)

            if pickings_to_warn:
                # Security Check
                if not self.env.user.has_group('stock_no_zero_cost.group_allow_zero_cost_move'):
                    raise UserError(_(
                        "You are not allowed to validate an Incoming or Internal stock move with a zero cost. "
                        "Please contact your stock manager to authorize this transfer."
                    ))

                # Show the Wizard to the authorized manager
                return {
                    'name': _('Zero Cost Valuation Warning (Transfer)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': {
                        'default_picking_id': pickings_to_warn[0].id,
                        'default_move_ids': [(6, 0, moves_to_warn.ids)],  # 3. Attention à la virgule ici !
                        'default_message': _(
                            "The following products have a 0.00 cost and will result in a zero valuation "
                            "for this transfer: \n- %s\n\n"
                            "Do you want to explicitly force this validation?"
                        ) % "\n- ".join(set(products_with_zero_cost))  # set() permet d'enlever les doublons
                    }
                }

        # Proceed with standard Odoo hooks (Backorder wizards, etc.)
        return super(StockPicking, self)._pre_action_done_hook()
