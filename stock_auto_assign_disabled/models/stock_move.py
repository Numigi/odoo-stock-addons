# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        disabled_status = self.env["ir.config_parameter"].get_param(
            "stock_auto_assign_disabled.config"
        )
        if disabled_status == "off":
            super()._action_assign()
        elif disabled_status == "serial":
            self_filtered = self.filtered(
                lambda x: x._should_process_auto_reservation()
            )
            super(StockMove, self_filtered)._action_assign()

    def _should_process_auto_reservation(self):
        return self.product_id.tracking != "serial"
