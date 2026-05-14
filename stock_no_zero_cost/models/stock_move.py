# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models, fields, _, tools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.move'

    zero_cost_approval_note = fields.Text(
        string="Zero Cost Approval Note",
        readonly=True,
        copy=False,
        help="Traces the user and date when a zero cost was explicitly approved."
    )

    def _action_done(self, cancel_backorder=False):
        """
        Hard block as a final defense line. It ensures programmatic validations
        cannot bypass the required manual approval wizard.
        """
        if tools.config['test_enable'] and not self.env.context.get(
            'force_zero_cost_check'
        ):
            return super(StockMove, self)._action_done(
                cancel_backorder=cancel_backorder
            )
        if not self.env.context.get('skip_zero_cost_check'):
            for move in self:
                company = move.company_id or self.env.company
                precision = company._get_zero_cost_precision_digits()
                if move.state not in ('done', 'cancel') and move.product_id.type == 'product':
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
                        raise UserError(_(
                            "Validation Blocked: Product '%s' has a zero cost (%s). "
                            "Please validate the transfer via the standard "
                            "interface to access the approval options, or "
                            "contact your inventory manager."
                        ) % (move.product_id.display_name, cost))

        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        note = self.env.context.get('zero_cost_approval_note')
        if note:
            res.write({'zero_cost_approval_note': note})

        return res
