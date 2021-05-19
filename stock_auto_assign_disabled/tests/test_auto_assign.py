# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestShadowMoves(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.stock_move = cls.env["stock.move"].create(
            {
                "name": "stock move",
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "product_id": cls.product.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
            }
        )

        cls.serial = cls.env["stock.production.lot"].create(
            {"name": cls.stock_move.name, "product_id": cls.product.id}
        )

        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "lot_id": cls.serial.id,
                "location_id": cls.stock_location.id,
                "quantity": 5,
                "package_id": None,
                "owner_id": None,
            }
        )

    def test_scheduler_no_reservation(self):
        self.stock_move._action_confirm()
        self.stock_move.group_id.run_scheduler()
        assert self.stock_move.reserved_availability == 0.0

    def test_scheduler_no_reservation_unconfirmed(self):
        self.stock_move.group_id.run_scheduler()
        assert self.stock_move.reserved_availability == 0.0
