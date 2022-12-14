# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class Warehouse(models.Model):

    _inherit = "stock.warehouse"

    rental_location_id = fields.Many2one(
        "stock.location",
        "Rental Stock Location",
        help="This location contains the stock available for rental.",
    )

    rental_route_id = fields.Many2one(
        "stock.location.route", "Rental Route", ondelete="restrict"
    )

    rental_type_id = fields.Many2one(
        "stock.picking.type", "Rental Picking Type", ondelete="restrict"
    )

    rental_return_type_id = fields.Many2one(
        "stock.picking.type", "Rental Return Picking Type", ondelete="restrict"
    )

    @api.model
    def create(self, vals):
        warehouse = super().create(vals)
        warehouse.setup_rental_route()
        return warehouse

    def setup_rental_route(self):
        self._create_rental_location()
        self._create_rental_picking_types()
        self._create_rental_route()

    def _create_rental_location(self):
        self.rental_location_id = self.env["stock.location"].create(
            {
                "name": _("Rental Stock"),
                "usage": "internal",
                "location_id": self.lot_stock_id.id,
                "company_id": self.company_id.id,
                "is_rental_stock_location": True,
            }
        )

    def _create_rental_route(self):
        vals = self._get_rental_route_values()
        vals["rule_ids"] = [
            (0, 0, self._get_rental_pull_values()),
            (0, 0, self._get_rental_return_push_values()),
        ]
        self.rental_route_id = self.env["stock.location.route"].create(vals)

    def _create_rental_picking_types(self):
        vals = self._get_rental_picking_type_create_values()
        self.rental_type_id = self.env["stock.picking.type"].create(vals)

        vals = self._get_rental_return_picking_type_create_values()
        self.rental_return_type_id = self.env["stock.picking.type"].create(vals)

        self._bind_rental_picking_types()

    def _get_rental_route_values(self):
        return {
            "name": "{warehouse}: Rental".format(warehouse=self.name),
            "active": True,
            "company_id": self.company_id.id,
            "product_categ_selectable": False,
            "warehouse_selectable": False,
            "product_selectable": False,
            "sequence": 10,
            "warehouse_ids": [(4, self.id)],
        }

    def _get_rental_pull_values(self):
        source_location = self.rental_location_id
        destination_location = self._get_rental_customer_location()
        return {
            "name": self._format_rulename(source_location, destination_location, ""),
            "location_src_id": source_location.id,
            "location_id": destination_location.id,
            "picking_type_id": self.rental_type_id.id,
            "action": "pull",
            "active": True,
            "company_id": self.company_id.id,
            "sequence": 1,
            "procure_method": "make_to_stock",
            "group_propagation_option": "propagate",
        }

    def _get_rental_return_push_values(self):
        source_location = self._get_rental_customer_location()
        destination_location = self.rental_location_id
        return {
            "name": self._format_rulename(source_location, destination_location, ""),
            "location_src_id": source_location.id,
            "location_id": destination_location.id,
            "picking_type_id": self.rental_return_type_id.id,
            "action": "push",
            "active": True,
            "company_id": self.company_id.id,
            "sequence": 100,
            "group_propagation_option": "propagate",
            "auto": "manual",
        }

    def _get_rental_picking_type_create_values(self):
        vals = self._get_rental_picking_type_values()
        vals.update(
            {
                "name": _("Rental"),
                "use_create_lots": True,
                "use_existing_lots": True,
                "sequence": 100,
                "sequence_code": "LRT",
                "sequence_id": self._create_rental_sequence().id,
            }
        )
        return vals

    def _get_rental_return_picking_type_create_values(self):
        vals = self._get_rental_return_picking_type_values()
        vals.update(
            {
                "name": _("Rental Return"),
                "use_create_lots": False,
                "use_existing_lots": False,
                "sequence_code": "LRTR",
                "sequence": 101,
                "sequence_id": self._create_rental_return_sequence().id,
            }
        )
        return vals

    def _bind_rental_picking_types(self):
        self.rental_type_id.return_picking_type_id = self.rental_return_type_id

    def _get_rental_picking_type_values(self):
        return {
            "warehouse_id": self.id,
            "code": "internal",
            "default_location_src_id": self.rental_location_id.id,
            "default_location_dest_id": self._get_rental_customer_location().id,
        }

    def _get_rental_return_picking_type_values(self):
        return {
            "warehouse_id": self.id,
            "code": "internal",
            "default_location_src_id": self._get_rental_customer_location().id,
            "default_location_dest_id": self.rental_location_id.id,
        }

    def _get_rental_customer_location(self):
        return self.env.ref("stock_rental.customer_location")

    def _create_rental_sequence(self):
        vals = self._get_rental_sequence_values()
        return self.env["ir.sequence"].create(vals)

    def _create_rental_return_sequence(self):
        vals = self._get_rental_return_sequence_values()
        return self.env["ir.sequence"].create(vals)

    def _get_rental_sequence_values(self):
        return {
            "name": "{}: Rental".format(self.name),
            "prefix": "{}/RT/".format(self.code),
            "padding": 5,
        }

    def _get_rental_return_sequence_values(self):
        return {
            "name": "{}: Rental Return".format(self.name),
            "prefix": "{}/RTR/".format(self.code),
            "padding": 5,
        }
