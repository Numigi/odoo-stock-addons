# Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        """
        Intercept the MO validation to check if produced items or consumed
        components have 0 cost.
        """
        # Bypass for standard Odoo tests to avoid breaking core modules
        if tools.config['test_enable'] and not self.env.context.get('force_zero_cost_check'):
            return super(MrpProduction, self).button_mark_done()

        if not self.env.context.get('skip_zero_cost_check'):
            productions_to_warn = self.env['mrp.production']
            products_with_zero_cost = []

            for mo in self:
                currency = mo.company_id.currency_id or self.env.company.currency_id

                # 1. Check the finished product
                if mo.product_id and mo.product_id.type == 'product':
                    cost = mo.product_id.standard_price
                    if float_is_zero(cost, precision_rounding=currency.rounding):
                        productions_to_warn |= mo
                        if mo.product_id.display_name:
                            products_with_zero_cost.append(mo.product_id.display_name)

                # 2. Check the raw materials (components)
                for raw_move in mo.move_raw_ids:
                    if (raw_move.product_id.type == 'product'
                            and raw_move.state not in ('done', 'cancel')):
                        comp_cost = raw_move.product_id.standard_price
                        if float_is_zero(comp_cost, precision_rounding=currency.rounding):
                            productions_to_warn |= mo
                            if raw_move.product_id.display_name:
                                products_with_zero_cost.append(raw_move.product_id.display_name)

            if productions_to_warn:
                # Clean the list to avoid duplicates
                products_names = ", ".join(filter(
                    None,
                    set(products_with_zero_cost))) or _("Unknown Product")

                group_xml = 'stock_no_zero_cost.group_allow_zero_cost_move'
                if not self.env.user.has_group(group_xml):
                    raise UserError(_(
                        "You are not allowed to validate a Manufacturing Order "
                        "yielding or consuming zero-cost products (%s). "
                        "Please contact your inventory manager."
                    ) % products_names)

                # Show Wizard for authorized managers
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
                            "You are about to produce or consume stockable products with a "
                            "cost of 0.00: \n- %s\n\n"
                            "Do you want to explicitly force this validation?"
                        ) % products_names
                    }
                }

        return super(MrpProduction, self).button_mark_done()
