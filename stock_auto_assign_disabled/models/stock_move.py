# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_process_auto_reservation(self):
        return self.product_id.tracking not in ["serial", "lot"]

    def _get_disabled_reservation_context(self):
        mode = self.env["ir.config_parameter"].sudo().get_param(
            "stock_auto_assign_disabled.config", "off"
        )
        is_scheduler = self._context.get("stock_auto_assign_disable")
        is_wizard = self._context.get("disable_reservation")

        if is_scheduler or is_wizard:
            if mode == "all":
                return {'disable_reservation': True}

        return {}

    def _filter_moves_for_auto_assign(self):
        ctx = self._get_disabled_reservation_context()
        if ctx.get('disable_reservation'):
            return self.with_context(**ctx)
        return self

    @api.multi
    def _action_confirm(self, merge=True, merge_into=False):
        ctx = self._get_disabled_reservation_context()
        if ctx.get('disable_reservation'):
            self = self.with_context(**ctx)

        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

    @api.multi
    def _action_assign(self):
        ctx = self._get_disabled_reservation_context()
        if ctx.get('disable_reservation') or self._context.get('disable_reservation'):
            _logger.info("STOCK_DISABLED: _action_assign bloqué par le contexte")
            # On stoppe l'action ici
            return True

        return super(StockMove, self)._action_assign()

    def _update_reserved_quantity(self, need, available_quantity, location_id,
                                  lot_id=None, package_id=None, owner_id=None, strict=True):

        ctx = self._get_disabled_reservation_context()
        if ctx.get('disable_reservation') or self._context.get('disable_reservation'):
            return 0.0

        return super(StockMove, self)._update_reserved_quantity(
            need, available_quantity, location_id, lot_id, package_id, owner_id, strict
        )