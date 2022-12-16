# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockPickingAddTransitCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type = cls.warehouse.out_type_id
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.product_a = cls.make_product("Product A")
        cls.product_b = cls.make_product("Product B")
        cls.transit_1 = cls.env["stock.location"].create(
            {
                "name": "Transit 1",
                "usage": "transit",
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.transit_2 = cls.env["stock.location"].create(
            {
                "name": "Transit 2",
                "usage": "transit",
                "company_id": cls.warehouse.company_id.id,
            }
        )

    @classmethod
    def make_quant(cls, location, product, quantity):
        cls.env["stock.quant"].create(
            {"location_id": location.id, "product_id": product.id, "quantity": quantity}
        )

    @classmethod
    def make_product(cls, name):
        return cls.env["product.product"].create({"name": name, "type": "product"})

    @classmethod
    def make_picking(cls, source, destination):
        return cls.env["stock.picking"].create(
            {
                "location_dest_id": destination.id,
                "location_id": source.id,
                "picking_type_id": cls.picking_type.id,
            }
        )

    @classmethod
    def make_stock_move(cls, picking, product, quantity):
        return cls.env["stock.move"].create(
            {
                "location_dest_id": picking.location_dest_id.id,
                "location_id": picking.location_id.id,
                "name": product.display_name,
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": quantity,
            }
        )

    @classmethod
    def make_stock_move_line(cls, move, quantity):
        return cls.env["stock.move.line"].create(
            {
                "location_dest_id": move.location_dest_id.id,
                "location_id": move.location_id.id,
                "move_id": move.id,
                "picking_id": move.picking_id.id,
                "product_id": move.product_id.id,
                "product_uom_id": move.product_uom.id,
                "qty_done": quantity,
                "product_uom_qty": 0,
            }
        )

    @classmethod
    def add_transit(cls, picking, location):
        wizard = cls.env["stock.picking.add.transit"].create(
            {"picking_id": picking.id, "location_id": location.id}
        )
        wizard.action_confirm()
