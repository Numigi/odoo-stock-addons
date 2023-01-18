# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

EXTERNAL_LOCATIONS = ("supplier", "customer")


class StockPickingAddTransit(models.TransientModel):

    _name = "stock.picking.add.transit"
    _description = "Stock Picking Add Transit Wizard"

    picking_id = fields.Many2one("stock.picking", "Picking")

    new_picking_id = fields.Many2one("stock.picking", "New Picking")

    location_id = fields.Many2one(
        "stock.location",
        "Location",
        domain="[('usage', 'in', ('internal', 'transit'))]",
    )

    @api.multi
    def action_confirm(self):
        self._check_picking_state()

        if self._should_add_transit_before():
            self._add_transit_before()
            action = self.new_picking_id.get_formview_action()
            action["target"] = "current"
            return action
        else:
            self._add_transit_after()

    def _check_picking_state(self):
        if self.picking_id.state == "draft":
            raise ValidationError(
                _("You must mark the picking as To Do before adding a transit.")
            )

        if self.picking_id.state in ("done", "cancel"):
            raise ValidationError(
                _("A transit can not be added if the picking is done or cancelled.")
            )

    def _should_add_transit_before(self):
        source_usage = self.picking_id.location_id.usage
        destination_usage = self.picking_id.location_dest_id.usage
        is_outgoing = (
            source_usage not in EXTERNAL_LOCATIONS
            and destination_usage in EXTERNAL_LOCATIONS
        )
        is_internal = (
            source_usage not in EXTERNAL_LOCATIONS
            and destination_usage not in EXTERNAL_LOCATIONS
        )
        return is_outgoing or is_internal

    def _add_transit_before(self):
        new_picking_vals = self._get_new_picking_vals_before()
        self.new_picking_id = self.env["stock.picking"].create(new_picking_vals)

        for old_move in self.picking_id.move_lines:
            self._create_move_before(old_move)

        self.picking_id.location_id = self.location_id
        self.picking_id.move_lines.write(
            {
                "state": "waiting",
                "procure_method": "make_to_order",
                "location_id": self.location_id.id,
            }
        )

    def _add_transit_after(self):
        new_picking_vals = self._get_new_picking_vals_after()
        self.new_picking_id = self.env["stock.picking"].create(new_picking_vals)

        for old_move in self.picking_id.move_lines:
            self._create_move_after(old_move)

        self.picking_id.location_dest_id = self.location_id
        self.picking_id.move_lines.write({"location_dest_id": self.location_id.id})
        self.picking_id.move_line_ids.write({"location_dest_id": self.location_id.id})

    def _get_new_picking_vals_before(self):
        vals = self._get_new_picking_vals()
        vals["location_id"] = self.picking_id.location_id.id
        vals["location_dest_id"] = self.location_id.id
        vals["partner_id"] = self._get_new_picking_partner_id(
            self.location_id).id,
        return vals

    def _get_new_picking_vals_after(self):
        vals = self._get_new_picking_vals()
        vals["location_id"] = self.location_id.id
        vals["location_dest_id"] = self.picking_id.location_dest_id.id
        vals["partner_id"] = self._get_new_picking_partner_id(
            self.picking_id.location_dest_id).id,
        return vals

    def _get_new_picking_vals(self):
        old_picking = self.picking_id
        return {
            "group_id": old_picking.group_id.id,
            "origin": old_picking.name,
            "move_type": old_picking.move_type,
            "priority": old_picking.priority,
            "scheduled_date": old_picking.scheduled_date,
            "company_id": old_picking.company_id.id,
            "picking_type_id": self._get_new_picking_type().id,
        }

    def _get_new_picking_partner_id(self, location_dest):
        partner_type = self.env["ir.config_parameter"].sudo().get_param(
            "stock_picking_add_transit.transit_partner_type"
        )
        if partner_type == 'warehouse':
            warehouse = self.location_id.get_warehouse()
            if not warehouse:
                warehouse = self.env["stock.warehouse"].search([
                    ('company_id', '=', self.picking_id.company_id.id)
                ])
            partner = warehouse.partner_id
        else:
            partner = self.picking_id.partner_id
        return partner

    def _get_new_picking_type(self):
        warehouse = self.picking_id.picking_type_id.warehouse_id
        if warehouse:
            return warehouse.int_type_id
        else:
            return self.env["stock.picking.type"].search(
                [
                    ("code", "=", "internal"),
                    ("warehouse_id.company_id", "=", self.picking_id.company_id.id),
                ],
                order="sequence",
                limit=1,
            )

    def _create_move_before(self, old_move):
        vals = self._get_move_before_vals(old_move)
        new_move = self.env["stock.move"].create(vals)
        new_move.move_orig_ids = old_move.move_orig_ids
        old_move.move_orig_ids = new_move
        self._transfer_old_move_lines_to_new_move(old_move, new_move)
        new_move.move_line_ids.write({"location_dest_id": new_move.location_dest_id.id})
        return new_move

    def _transfer_old_move_lines_to_new_move(self, old_move, new_move):
        old_move.move_line_ids.write(
            {"picking_id": new_move.picking_id.id, "move_id": new_move.id}
        )

    def _create_move_after(self, old_move):
        vals = self._get_move_after_vals(old_move)
        new_move = self.env["stock.move"].create(vals)
        new_move.move_dest_ids = old_move.move_dest_ids
        old_move.move_dest_ids = new_move
        return new_move

    def _get_move_before_vals(self, old_move):
        vals = self._get_move_vals(old_move)
        vals["state"] = old_move.state
        vals["location_id"] = old_move.location_id.id
        vals["location_dest_id"] = self.location_id.id
        return vals

    def _get_move_after_vals(self, old_move):
        vals = self._get_move_vals(old_move)
        vals["state"] = "waiting"
        vals["location_id"] = self.location_id.id
        vals["location_dest_id"] = old_move.location_dest_id.id
        return vals

    def _get_move_vals(self, old_move):
        return {
            "group_id": old_move.group_id.id,
            "product_id": old_move.product_id.id,
            "product_uom_qty": old_move.product_uom_qty,
            "product_uom": old_move.product_uom.id,
            "origin": old_move.origin,
            "propagate": old_move.propagate,
            "route_ids": [(4, id_) for id_ in old_move.route_ids.ids],
            "restrict_partner_id": old_move.restrict_partner_id.id,
            "company_id": old_move.company_id.id,
            "date": old_move.date,
            "date_expected": old_move.date_expected,
            "priority": old_move.priority,
            "sequence": old_move.sequence,
            "name": old_move.name,
            "procure_method": "make_to_stock",
            "picking_type_id": self.new_picking_id.picking_type_id.id,
            "picking_id": self.new_picking_id.id,
        }
