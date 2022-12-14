# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from .stock_production_lot import PULLING_COMPONENTS


class StockMove(models.Model):

    _inherit = "stock.move"

    child_ids = fields.One2many("stock.move", "parent_id", "Component Moves")

    parent_id = fields.Many2one("stock.move", "Parent Move")

    def _should_be_assigned(self):
        if self.parent_id:
            return False
        return super()._should_be_assigned()

    def _action_done(self):
        self_sudo = self.sudo().with_context(lang=self.env.user.lang)
        if not self_sudo._is_pulling_components():
            self_sudo._check_no_component_moved()

        res = super()._action_done()

        moves_with_components = self_sudo.filtered(
            lambda m: m._has_components() and m.state == "done"
        )
        for move in moves_with_components:
            move.generate_component_moves()

        return res

    def _has_components(self):
        return bool(
            self.product_id.tracking == "serial"
            and self.mapped("move_line_ids.lot_id.component_line_ids")
        )

    def generate_component_moves(self):
        for line in self.mapped("move_line_ids"):
            line.generate_component_moves()

    def _is_pulling_components(self):
        return self._context.get(PULLING_COMPONENTS, False)

    def _check_no_component_moved(self):
        serials = self.mapped("move_line_ids.lot_id")
        components = serials.filtered(lambda s: s.is_component)

        if components:
            message = _(
                "You are attempting to move products that are components "
                "of an equipment."
            )
            details = "\n".join(
                self._get_component_serial_not_movable_message(s) for s in components
            )
            raise ValidationError("\n".join((message, details)))

    def _get_component_serial_not_movable_message(self, serial):
        return _(
            "The product {product} with serial number {serial} is a "
            "component of {parent}."
        ).format(
            product=serial.product_id.display_name,
            serial=serial.display_name,
            parent=serial.parent_component_id.display_name,
        )
