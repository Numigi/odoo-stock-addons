from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        """
        Intercept the MO validation to check if produced items have 0 cost.
        """
        if not self.env.context.get('skip_zero_cost_check'):
            productions_to_warn = self.env['mrp.production']
            products_with_zero_cost = []

            for mo in self:
                # Check only finished products being produced
                for move in mo.move_finished_ids.filtered(
                        lambda m: m.state not in ('done', 'cancel') and m.product_id.type == 'product'):
                    currency = mo.company_id.currency_id or self.env.company.currency_id
                    # For MO, the cost entering stock is the price_unit if calculated, otherwise standard_price
                    cost = move.price_unit if move.price_unit else move.product_id.standard_price

                    if float_is_zero(cost, precision_rounding=currency.rounding):
                        productions_to_warn |= mo
                        products_with_zero_cost.append(move.product_id.display_name)

            if productions_to_warn:
                # Security Check
                if not self.env.user.has_group('stock_no_zero_cost.group_allow_zero_cost_move'):
                    raise UserError(_(
                        "You are not allowed to validate a Manufacturing Order yielding zero-cost products (%s). "
                        "Please contact your inventory manager."
                    ) % ", ".join(set(products_with_zero_cost)))

                # Show Wizard
                return {
                    'name': _('Zero Cost Valuation Warning (Manufacturing)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_production_id': productions_to_warn[0].id,
                        'default_message': _(
                            "You are about to produce stockable products with a cost of 0.00: \n- %s\n\n"
                            "Do you want to explicitly force this validation?"
                        ) % "\n- ".join(set(products_with_zero_cost))
                    }
                }

        return super(MrpProduction, self).button_mark_done()
