# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class StockRentalConversionWizard(models.TransientModel):

    _name = "stock.rental.conversion.wizard"
    _description = "Stock Rental Conversion Wizard"

    sales_product_id = fields.Many2one("product.product")
    sales_lot_id = fields.Many2one("stock.production.lot")
    sales_product_move_id = fields.Many2one("stock.move")
    rental_product_id = fields.Many2one("product.product")
    rental_lot_id = fields.Many2one("stock.production.lot")
    rental_product_move_id = fields.Many2one("stock.move")
    source_location_id = fields.Many2one("stock.location")
    destination_location_id = fields.Many2one("stock.location")
    is_serialized_product = fields.Boolean(compute="_compute_is_serialized_product")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)

        active_model = self._context.get("active_model")
        active_id = self._context.get("active_id")

        if active_model == "product.template":
            template = self.env["product.template"].browse(active_id)
            vals["sales_product_id"] = template.product_variant_ids[:1].id
        elif active_model == "product.product":
            vals["sales_product_id"] = active_id

        return vals

    @api.depends("sales_product_id")
    @api.onchange("sales_product_id")
    def _compute_is_serialized_product(self):
        for wizard in self:
            wizard.is_serialized_product = wizard.sales_product_id.tracking == "serial"

    @api.onchange("sales_product_id")
    def _empty_serial_if_unrelated_to_rental_product(self):
        if self.sales_product_id != self.sales_lot_id.product_id:
            self.sales_lot_id = False

    @api.onchange("sales_product_id")
    def _set_rental_product_from_sales_product(self):
        self.rental_product_id = self.sales_product_id.rental_product_id

    @api.onchange("sales_lot_id")
    def _set_locations_from_selected_serial_number(self):
        if self.sales_lot_id:
            self.source_location_id = self.sales_lot_id.get_current_location()[:1]

    @api.onchange("source_location_id")
    def _set_destination_location_as_rental_stock_location(self):
        if self.source_location_id:
            source_warehouse = self.source_location_id.get_warehouse()
            self.destination_location_id = source_warehouse.rental_location_id

    def validate(self):
        self._move_sales_product()

        if self.sales_lot_id:
            self._create_rental_lot()

        self._move_rental_product()

    def _move_sales_product(self):
        move_vals = self._get_sales_move_vals()
        move = self.env["stock.move"].create(move_vals)
        move_line_vals = self._get_sales_move_line_vals(move)
        self.env["stock.move.line"].create(move_line_vals)
        move._action_done()
        self.sales_product_move_id = move

    def _move_rental_product(self):
        move_vals = self._get_rental_move_vals()
        move = self.env["stock.move"].create(move_vals)
        move_line_vals = self._get_rental_move_line_vals(move)
        self.env["stock.move.line"].create(move_line_vals)
        move._action_done()
        self.rental_product_move_id = move

    def _create_rental_lot(self):
        self.rental_lot_id = self.env["stock.production.lot"].create(
            {
                "location_id": self.source_location_id.id,
                "product_id": self.rental_product_id.id,
                "name": self.sales_lot_id.name,
                "ref": self.sales_lot_id.ref,
                "quantity": 1,
                "sales_lot_id": self.sales_lot_id.id,
            }
        )

    def _get_sales_move_vals(self):
        return {
            "company_id": self.source_location_id.company_id.id,
            "location_dest_id": self._get_production_location().id,
            "location_id": self.source_location_id.id,
            "name": self._get_move_name(),
            "product_id": self.sales_product_id.id,
            "product_uom": self._get_uom().id,
            "product_uom_qty": 1,
            "state": "confirmed",
        }

    def _get_sales_move_line_vals(self, move):
        return {
            "location_dest_id": self._get_production_location().id,
            "location_id": self.source_location_id.id,
            "lot_id": self.sales_lot_id.id,
            "move_id": move.id,
            "package_id": self.sales_lot_id.get_current_package().id,
            "product_id": self.sales_product_id.id,
            "product_uom_id": self._get_uom().id,
            "product_uom_qty": 0,
            "qty_done": 1,
        }

    def _get_rental_move_vals(self):
        return {
            "company_id": self.destination_location_id.company_id.id,
            "location_id": self._get_production_location().id,
            "location_dest_id": self.destination_location_id.id,
            "name": self._get_move_name(),
            "product_id": self.rental_product_id.id,
            "product_uom": self._get_uom().id,
            "product_uom_qty": 1,
            "state": "confirmed",
        }

    def _get_rental_move_line_vals(self, move):
        return {
            "location_id": self._get_production_location().id,
            "location_dest_id": self.destination_location_id.id,
            "lot_id": self.rental_lot_id.id,
            "move_id": move.id,
            "product_id": self.rental_product_id.id,
            "product_uom_id": self._get_uom().id,
            "product_uom_qty": 0,
            "qty_done": 1,
        }

    def _get_uom(self):
        return self.env.ref("uom.product_uom_unit")

    def _get_move_name(self):
        return _("Conversion of {sales_product} to {rental_product} ({serial})").format(
            sales_product=self.sales_product_id.display_name,
            rental_product=self.rental_product_id.display_name,
            serial=self.sales_lot_id.name,
        )

    def _get_production_location(self):
        return self.env.ref("stock.location_production")
