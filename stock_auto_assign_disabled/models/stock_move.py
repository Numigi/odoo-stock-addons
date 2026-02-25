# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_process_auto_reservation(self):
        return self.product_id.tracking not in ["serial", "lot"]

    def _filter_moves_for_auto_assign(self):
        """
        Filtre les mouvements ou applique le contexte d'interdiction.
        """
        mode = self.env["ir.config_parameter"].sudo().get_param(
            "stock_auto_assign_disabled.config", "off"
        )
        is_scheduler = self._context.get("stock_auto_assign_disable")
        is_wizard = self._context.get("disable_reservation")

        if is_scheduler or is_wizard:
            if mode == "all":
                return self.with_context(disable_reservation=True)
            elif mode == "serial_lot":
                # On filtre et on retire les articles tracés par lot/série (les tests refonctionneront)
                return self.filtered(lambda x: x._should_process_auto_reservation())

        return self

    @api.multi
    def _action_confirm(self, merge=True, merge_into=False):
        # Pour contrer la réservation immédiate au moment de la confirmation
        mode = self.env["ir.config_parameter"].sudo().get_param(
            "stock_auto_assign_disabled.config", "off"
        )
        is_scheduler = self._context.get("stock_auto_assign_disable")
        is_wizard = self._context.get("disable_reservation")

        if (is_scheduler or is_wizard) and mode == "all":
            self = self.with_context(disable_reservation=True)

        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

    @api.multi
    def _action_assign(self):
        # On applique le filtre (qui gère 'all' et 'serial_lot')
        moves_to_assign = self._filter_moves_for_auto_assign()

        if moves_to_assign._context.get('disable_reservation'):
            return True  # On simule le succès sans appeler le super()

        return super(StockMove, moves_to_assign)._action_assign()

    def _update_reserved_quantity(self, need, available_quantity, location_id,
                                  lot_id=None, package_id=None, owner_id=None, strict=True):
        """
        Protection de bas niveau (La porte de sortie).
        """
        mode = self.env["ir.config_parameter"].sudo().get_param("stock_auto_assign_disabled.config", "off")
        is_scheduler = self._context.get("stock_auto_assign_disable")
        is_wizard = self._context.get("disable_reservation")

        if is_scheduler or is_wizard:
            if mode == "all":
                return 0.0
            elif mode == "serial_lot" and not self._should_process_auto_reservation():
                return 0.0

        return super(StockMove, self)._update_reserved_quantity(
            need, available_quantity, location_id, lot_id, package_id, owner_id, strict
        )
