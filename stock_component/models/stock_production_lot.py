# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    component_ids = fields.Many2many(
        "stock.production.lot",
        string="Components",
        compute="_compute_child_components",
    )

    component_line_ids = fields.One2many(
        "stock.component.line", "parent_component_id", "Component Lines",
    )

    parent_component_id = fields.Many2one(
        "stock.production.lot", "Parent Component", compute="_compute_parent_component"
    )

    @api.depends("component_line_ids.component_id")
    def _compute_child_components(self):
        for serial in self:
            serial.component_ids = serial.mapped("component_line_ids.component_id")

    def _compute_parent_component(self):
        for serial in self:
            serial.parent_component_id = serial._get_parent_component()

    def _get_parent_component(self):
        return self.env["stock.production.lot"].search(
            [("component_line_ids.component_id", "=", self.id)], limit=1
        )

    def add_component(self, serial):
        self._check_component_can_be_added(serial)
        self._move_component_if_in_child_location(serial)
        self._create_component_line(serial)

    def _check_component_can_be_added(self, serial):
        try:
            self._check_component_can_be_added_constraints(serial)
        except ValidationError as err:
            generic_message = _(
                "The serial number {serial} can not be added as component "
                "to the equipment {parent}."
            ).format(serial=serial.display_name, parent=self.display_name)
            raise ValidationError("{}\n\n{}".format(generic_message, err.name))

    def _check_component_can_be_added_constraints(self, serial):
        self._check_has_one_non_null_quant()
        serial._check_has_one_non_null_quant()
        self._check_has_not_child_component(serial)
        serial._check_has_no_parent_component()
        self._check_component_in_same_or_child_location(serial)
        self._check_component_not_in_different_package(serial)
        self._check_component_has_not_different_owner(serial)
        serial._check_is_not_reserved()

    def _check_has_not_child_component(self, serial):
        if serial in self.component_ids:
            raise ValidationError(
                _(
                    "The serial number {serial} is already part of the equipment "
                    "({parent})."
                ).format(
                    serial=serial.display_name, parent=self.display_name,
                )
            )

    def _check_has_no_parent_component(self):
        if self._get_parent_component():
            raise ValidationError(
                _(
                    "The serial number {serial} is already a component of an equipment "
                    "({parent}). A component can not be part of 2 different equipments."
                ).format(
                    serial=self.display_name,
                    parent=self.parent_component_id.display_name,
                )
            )

    def _check_has_one_non_null_quant(self):
        quants = self.get_non_zero_quants()
        if len(quants) > 1:
            message = _(
                "The serial number {serial} is linked to more than one quant:"
            ).format(serial=self.display_name)
            quant_names = quants.mapped("display_name")
            raise ValidationError(
                "{}:\n\n *{}".format(message, "\n *".join(quant_names))
            )

        if len(quants) < 1:
            raise ValidationError(
                _("The serial number {serial} is not linked to a quant.").format(
                    serial=self.display_name
                )
            )

    def _check_component_in_same_or_child_location(self, serial):
        serial_location = serial.get_current_location()
        parent_location = self.get_current_location()

        same_or_child_location = (
            serial_location == parent_location
            or self._is_component_in_child_location(serial)
        )

        if not same_or_child_location:
            raise ValidationError(
                _(
                    "The selected serial number is in the location {serial_location}.\n"
                    "The equipment is in another location ({parent_location})."
                ).format(
                    serial_location=serial_location.display_name,
                    parent_location=parent_location.display_name,
                )
            )

    def _check_component_not_in_different_package(self, serial):
        parent_package = self.get_non_zero_quants().package_id
        serial_package = serial.get_non_zero_quants().package_id

        if not parent_package and serial_package:
            raise ValidationError(
                _("The selected serial number is in a package ({package}).").format(
                    package=serial_package.display_name,
                )
            )

        if parent_package and serial_package and parent_package != serial_package:
            raise ValidationError(
                _(
                    "The selected serial number is in the package {package}.\n"
                    "The equipment is in a different package ({parent_package})."
                ).format(
                    package=serial_package.display_name,
                    parent_package=parent_package.display_name,
                )
            )

    def _check_component_has_not_different_owner(self, serial):
        parent_owner = self.get_non_zero_quants().owner_id
        serial_owner = serial.get_non_zero_quants().owner_id

        if not parent_owner and serial_owner:
            raise ValidationError(
                _("The selected serial number has the owner ({owner}).").format(
                    owner=serial_owner.display_name,
                )
            )

        if parent_owner and serial_owner and parent_owner != serial_owner:
            raise ValidationError(
                _(
                    "The selected serial number has the owner {owner}.\n"
                    "The equipment has a different owner ({parent_owner})."
                ).format(
                    owner=serial_owner.display_name,
                    parent_owner=parent_owner.display_name,
                )
            )

    def _check_is_not_reserved(self):
        if self.get_non_zero_quants().reserved_quantity:
            raise ValidationError(
                _(
                    "The selected serial number is reserved by a stock move.\n"
                    "It can not be added as a component."
                )
            )

    def _create_component_line(self, serial):
        self.env["stock.component.line"].create(
            {"parent_component_id": self.id, "component_id": serial.id,}
        )

    def _move_component_if_in_child_location(self, serial):
        if self._is_component_in_child_location(serial):
            self._move_component_to_equipment_location(serial)

    def _is_component_in_child_location(self, serial):
        serial_location = serial.get_current_location()
        parent_location = self.get_current_location()
        return serial_location.is_child_of(parent_location)

    def _move_component_to_equipment_location(self, serial):
        move = self.env["stock.move"].create(self._get_component_move_vals(serial))
        self.env["stock.move.line"].create(
            self._get_component_move_line_vals(move, serial)
        )
        move._action_done()

    def _get_common_component_move_vals(self, serial):
        return {
            "product_id": serial.product_id.id,
            "location_id": serial.get_current_location().id,
            "location_dest_id": self.get_current_location().id,
        }

    def _get_component_move_vals(self, serial):
        vals = self._get_common_component_move_vals(serial)
        vals.update(
            {
                "name": self._get_component_move_name(serial),
                "product_uom_qty": 1,
                "product_uom": self._get_component_uom().id,
            }
        )
        return vals

    def _get_component_move_line_vals(self, move, serial):
        vals = self._get_common_component_move_vals(serial)
        vals.update(
            {
                "move_id": move.id,
                "lot_id": serial.id,
                "qty_done": 1,
                "product_uom_qty": 0,
                "product_uom_id": self._get_component_uom().id,
            }
        )
        return vals

    def _get_component_uom(self):
        return self.env.ref("uom.product_uom_unit")

    def _get_component_move_name(self, serial):
        return _("Move component {serial} as part of equipment {parent}").format(
            serial=serial.display_name, parent=self.display_name
        )

    def get_current_location(self):
        return self.get_non_zero_quants().location_id

    def get_non_zero_quants(self):
        return self.mapped("quant_ids").filtered(lambda q: q.quantity)
