# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_validate(self):
        """
        Intercept Inventory Adjustment to prevent incoming positive stock at 0 cost.
        """
        if tools.config['test_enable'] and not self.env.context.get(
            'force_zero_cost_check'
        ):
            return super(StockInventory, self).action_validate()

        if not self.env.context.get('skip_zero_cost_check'):
            inventories_to_warn = self.env['stock.inventory']
            products_with_zero_cost = []

            for inventory in self:
                for line in inventory.line_ids:
                    # We only care about stockable products that INCREASE
                    if (
                        line.product_id.type == 'product'
                        and line.product_qty > line.theoretical_qty
                    ):
                        currency = (
                            inventory.company_id.currency_id
                            or self.env.company.currency_id
                        )
                        cost = line.product_id.standard_price
                        if float_is_zero(cost, precision_rounding=currency.rounding):
                            inventories_to_warn |= inventory
                            products_with_zero_cost.append(line.product_id.display_name)

            if inventories_to_warn:
                group_xml = 'stock_no_zero_cost.group_allow_zero_cost_move'
                if not self.env.user.has_group(group_xml):
                    raise UserError(_(
                        "You cannot validate an inventory adjustment creating positive "
                        "stock for zero-cost products (%s). Please either update the "
                        "product cost on the product form first, or ask your stock "
                        "manager to validate this adjustment."
                    ) % ", ".join(set(products_with_zero_cost)))

                return {
                    'name': _('Zero Cost Valuation Warning (Inventory)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': {
                        'default_inventory_id': inventories_to_warn[0].id,
                        'default_message': _(
                            "The following products have a 0.00 cost and will result "
                            "in a zero valuation for the newly discovered stock: "
                            "\n- %s\n\nDo you want to explicitly force this validation?"
                        ) % "\n- ".join(set(products_with_zero_cost))
                    }
                }

        return super(StockInventory, self).action_validate()
