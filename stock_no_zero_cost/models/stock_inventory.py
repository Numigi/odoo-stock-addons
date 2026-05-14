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
                        company = (
                            inventory.company_id
                            or self.env.company
                        )
                        precision = company._get_zero_cost_precision_digits()
                        cost = line.product_id.standard_price
                        if float_is_zero(cost, precision_digits=precision):
                            inventories_to_warn |= inventory
                            products_with_zero_cost.append(
                                "%s (Cost: %s)" % (line.product_id.display_name, cost)
                            )

            if inventories_to_warn:
                message = _("The following products have a 0.00 cost and will "
                            "result in a zero valuation for the newly discovered stock: \n"
                            "\n- %s"
                            ) % "\n- ".join(set(products_with_zero_cost))
                group_xml = 'stock_no_zero_cost.group_allow_zero_cost_move'
                if not self.env.user.has_group(group_xml):
                    raise UserError(message + _(
                        "\n \n You cannot validate an inventory adjustment  "
                        "with prodcuts having zero cost. \n"
                        "Please either update the product cost first ,"
                        "or ask your stock manager to validate this adjustment."))

                return {
                    'name': _('Zero Cost Valuation Warning (Inventory)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.zero.cost.wizard',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': {
                        'default_inventory_id': inventories_to_warn[0].id,
                        'default_message': message + _(
                            "\n\nDo you want to explicitly force this validation?"
                        )
                    }
                }

        return super(StockInventory, self).action_validate()
