# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_process_auto_reservation(self):
        return self.product_id.tracking not in ["serial", "lot"]

    def _filter_moves_for_auto_assign(self):
        """
        Apply disable logic config and return the recordset to process.
        If mode is 'all', context is updated on the returned recordset.
        """
        mode = self.env["ir.config_parameter"].sudo().get_param(
            "stock_auto_assign_disabled.config", "off"
        )
        stock_auto_assign_disable = self._context.get("stock_auto_assign_disable")
        is_superuser = self.env.user == self.env.ref('base.user_root')

        if stock_auto_assign_disable or is_superuser :
            if mode == "all":
                # Return self with the flag in context.
                # The caller will use this recordset which already carries the context.
                return self.with_context(disable_reservation=True)
            elif mode == "serial_lot":
                return self.filtered(lambda x: x._should_process_auto_reservation())

        return self

    def _action_assign(self):
        moves_to_assign = self._filter_moves_for_auto_assign()
        return super(StockMove, moves_to_assign)._action_assign()
