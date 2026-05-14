# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _pre_action_done_hook(self):
        if tools.config['test_enable'] and not self.env.context.get(
            'force_zero_cost_check'
        ):
            return super(StockPicking, self)._pre_action_done_hook()
        # If the context tells us to skip, we bypass
        if not self.env.context.get('skip_zero_cost_check'):
            company = self.company_id or self.env.company
            precision = company._get_zero_cost_precision_digits()
            pickings_to_warn = self.env['stock.picking']
            moves_to_warn = self.env['stock.move']
            products_with_zero_cost = []

            for picking in self:
                for move in picking.move_lines:
                    # Filter: Only stockable products, incoming/internal,
                    # and not yet done/cancelled
                    if (move.state not in ('done', 'cancel')
                            and move.product_id.type == 'product'):
                        company = move.company_id or self.env.company
                        check_cost = False
                        cost = move.product_id.standard_price
                        # Purchase   (Always bloc)
                        if move.location_id.usage == 'supplier':
                            check_cost = True
                            cost = move.price_unit
                        # Inventory  (Always bloc)
                        elif move.location_id.usage == 'inventory':
                            check_cost = True
                        # 3. consumption (config)
                        elif move.location_dest_id.usage == 'production':
                            check_cost = company.check_zero_cost_consumption
                        # 4. PRODUCTION (config)
                        elif move.location_id.usage == 'production':
                            check_cost = company.check_zero_cost_production
                        # 5. Internal (config)
                        elif (move.location_id.usage == 'internal'
                              and move.location_dest_id.usage == 'internal'):
                            check_cost = company.check_zero_cost_internal

                        if check_cost and float_is_zero(cost, precision_digits=precision):
                            pickings_to_warn |= picking
                            moves_to_warn |= move
                            products_with_zero_cost.append(
                                "%s (Cost: %s)" % (move.product_id.display_name, cost)
                            )

            if pickings_to_warn:
                # Security Check
                message = _("The following products have a 0.00 cost and will "
                            "result in a zero valuation for this transfer: \n"
                            "\n- %s"
                            ) % "\n- ".join(set(products_with_zero_cost))
                group_xml = 'stock_no_zero_cost.group_allow_zero_cost_move'
                if not self.env.user.has_group(group_xml):
                    raise UserError(message + _(
                        "\n \n You are not allowed to validate this picking "
                        "with prodcuts having zero cost. \n "
                        " Please either update the product cost first ,"
                        "or ask your stock manager to validate this internal picking"
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
                        'default_move_ids': [(6, 0, moves_to_warn.ids)],
                        'default_message': message + _(
                            "\n\nDo you want to explicitly force this validation?")
                    }
                }

        return super(StockPicking, self)._pre_action_done_hook()
