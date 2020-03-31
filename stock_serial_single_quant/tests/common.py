# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class StockMoveCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.warehouse_1 = cls.make_warehouse("W1")
        cls.warehouse_2 = cls.make_warehouse("W2")
        cls.warehouse_3 = cls.make_warehouse("W3")

        cls.product_1 = cls.make_product("P1")
        cls.product_2 = cls.make_product("P2")
        cls.product_3 = cls.make_product("P3")

        cls.serial_1 = cls.make_serial_number("S1", cls.product_1)
        cls.serial_2 = cls.make_serial_number("S2", cls.product_2)
        cls.serial_3 = cls.make_serial_number("S3", cls.product_2)

        cls.location_1 = cls.warehouse_1.lot_stock_id
        cls.location_2 = cls.warehouse_2.lot_stock_id
        cls.location_3 = cls.warehouse_3.lot_stock_id

        cls.location_1a = cls.make_location(cls.location_1, "A")
        cls.location_1aa = cls.make_location(cls.location_1a, "AA")

        cls.package_1 = cls.make_package("P1", cls.location_1)
        cls.package_2 = cls.make_package("P2", cls.location_1)

        cls.owner_1 = cls.make_owner("Owner 1")
        cls.owner_2 = cls.make_owner("Owner 2")

    def move_serial_number(
        self,
        serial,
        location_src,
        location_dest,
        package_src=None,
        package_dest=None,
        owner_src=None,
    ):
        move = self.env["stock.move"].create(
            {
                "product_id": serial.product_id.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "name": "/",
                "product_uom_qty": 1,
                "product_uom": self.uom_unit.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "product_id": serial.product_id.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "move_id": move.id,
                "lot_id": serial.id,
                "qty_done": 1,
                "product_uom_qty": 0,
                "product_uom_id": self.uom_unit.id,
                "package_id": package_src.id if package_src else None,
                "result_package_id": package_dest.id if package_dest else None,
                "owner_id": owner_src.id if owner_src else None,
            }
        )
        move._action_done()

    @classmethod
    def make_product(cls, name):
        return cls.env["product.product"].create(
            {"name": name, "type": "product", "tracking": "serial"}
        )

    @classmethod
    def make_serial_number(cls, name, product):
        return cls.env["stock.production.lot"].create(
            {"name": name, "product_id": product.id}
        )

    @classmethod
    def make_location(cls, parent, name):
        return cls.env["stock.location"].create(
            {"name": name, "location_id": parent.id, "usage": "internal"}
        )

    @classmethod
    def make_quant(cls, location, serial, package=None, owner=None):
        return cls.env["stock.quant"].create(
            {
                "product_id": serial.product_id.id,
                "lot_id": serial.id,
                "location_id": location.id,
                "quantity": 1,
                "package_id": package.id if package else None,
                "owner_id": owner.id if owner else None,
            }
        )

    @classmethod
    def make_package(cls, name, location):
        return cls.env["stock.quant.package"].create(
            {"name": name, "location_id": location.id}
        )

    @classmethod
    def make_owner(cls, name):
        return cls.env["res.partner"].create({"name": name})

    @classmethod
    def make_warehouse(cls, name):
        return cls.env["stock.warehouse"].create({"name": name, "code": name})
