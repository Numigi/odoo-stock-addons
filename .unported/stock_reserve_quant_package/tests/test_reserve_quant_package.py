# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestReservePackage(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {"name": "Testing",
             "email": "testing@testmail.com",
             "login": "Testing"}
        )
        cls.user.groups_id = cls.env.ref("stock.group_stock_user")

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_B = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.stock_move_A = cls.env["stock.move"].create(
            {
                "name": "stock move",
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "product_id": cls.product_A.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1.0,
            }
        )
        cls.stock_move_B = cls.env["stock.move"].create(
            {
                "name": "stock move",
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "product_id": cls.product_B.id,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 2.0,
            }
        )

        cls.group = cls.stock_move_A.group_id

        cls.package_A = cls.env["stock.quant.package"].create(
            {"name": 'PACK0000001', "location_id": cls.stock_location.id}
        )
        cls.package_B = cls.env["stock.quant.package"].create(
            {"name": 'PACK0000002', "location_id": cls.stock_location.id}
        )

        cls.quant_A = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_A.id,
                "location_id": cls.stock_location.id,
                "quantity": 2,
                "package_id": cls.package_A.id,
                "owner_id": None,
            }
        )
        cls.quant_B = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_B.id,
                "location_id": cls.stock_location.id,
                "quantity": 2,
                "package_id": cls.package_B.id,
                "owner_id": None,
            }
        )

    def test_move_all_package(self):
        self.stock_move_A._action_confirm()
        self.stock_move_B._action_confirm()
        self._run_scheduler(self.group, self.user)
        assert self.stock_move_A.reserved_availability == 0.0
        assert self.stock_move_B.reserved_availability == 2.0

    def _run_scheduler(self, group, user):
        group.sudo(user).run_scheduler()
