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
        # --- BYPASS POUR LES TESTS STANDARDS ODOO ---
        if tools.config['test_enable'] and not self.env.context.get(
            'force_zero_cost_check'
        ):
            return super(StockMove, self)._action_done(
                cancel_backorder=cancel_backorder
            )

        if not self.env.context.get('skip_zero_cost_check'):
            for move in self:
                if move.state not in ('done', 'cancel') and move.product_id.type == 'product':
                    if move.location_dest_id.usage in ('internal', 'production'):
                        currency = move.company_id.currency_id or self.env.company.currency_id
                        cost = move.price_unit if move._is_in() else move.product_id.standard_price

                        if float_is_zero(cost, precision_rounding=currency.rounding):
                            raise UserError(_(
                                "Validation Blocked: Product '%s' has a zero cost. "
                                "Please validate the transfer via the standard "
                                "interface to access the approval options, or "
                                "contact your inventory manager."
                            ) % move.product_id.display_name)

        return super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
