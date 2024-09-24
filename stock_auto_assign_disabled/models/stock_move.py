# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_process_auto_reservation(self):
        return self.product_id.tracking not in ["serial", "lot"]

    def _action_assign(self):
        mode = self.env["ir.config_parameter"].sudo().get_param(
            "stock_auto_assign_disabled.config", "off"
        )
        stock_auto_assign_disable = self._context.get("stock_auto_assign_disable")
        if stock_auto_assign_disable:
            if mode == "all":
                self = self.with_context(disable_reservation=True)
            elif mode == "serial_lot":
                self_filtered = self.filtered(
                    lambda x: x._should_process_auto_reservation()
                )
                self = self_filtered
        return super(StockMove, self)._action_assign()
