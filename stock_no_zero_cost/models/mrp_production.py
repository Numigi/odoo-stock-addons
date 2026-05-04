# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        """
        Intercept the MO validation to check if produced items have 0 cost.
        """
        # --- BYPASS POUR LES TESTS STANDARDS ODOO ---
        if tools.config['test_enable'] and not self.env.context.get(
            'force_zero_cost_check'
        ):
            return super(MrpProduction, self).button_mark_done()

        if not self.env.context.get('skip_zero_cost_check'):
            productions_to_warn = self.env['mrp.production']
            products_with_zero_cost = []

            for mo in self:
                # Check only finished products being produced
                finished_moves = mo.move_finished_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                    and m.product_id.type == 'product'
                )
                for move in finished_moves:
                    currency = (
                        mo.company_id.currency_id or self.env.company.currency_id
                    )
                    cost = (
                        move.price_unit if move.price_unit
                        else move.product_id.standard_price
                    )

                    if float_is_zero(cost, precision_rounding=currency.rounding):
                        productions_to_warn |= mo
                        products_with_zero_cost.append(move.product_id.display_name)

            if productions_to_warn:
                # Security Check
                group_xml = 'stock_no_zero_cost.group_allow_zero_cost_move'
                if not self.env.user.has_group(group_xml):
                    raise UserError(_(
                        "You are not allowed to validate a Manufacturing Order "
                        "yielding zero-cost products (%s). "
                        "Please contact your inventory manager."
                    ) % ", ".join(set(products_with_zero_cost)))

                # Show Wizard
                return {
                    'name': _('Zero Cost Valuation Warning (Manufacturing)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': {
                        'default_production_id': productions_to_warn[0].id,
                        'default_message': _(
                            "You are about to produce stockable products with a "
                            "cost of 0.00: \n- %s\n\n"
                            "Do you want to explicitly force this validation?"
                        ) % "\n- ".join(set(products_with_zero_cost))
                    }
                }

        return super(MrpProduction, self).button_mark_done()
