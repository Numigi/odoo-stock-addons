# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAutoAssignDisabledJit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {"name": "Testing", "email": "testing@testmail.com", "login": "Testing"}
        )
        cls.user.groups_id = cls.env.ref("sales_team.group_sale_salesman")

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner",
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "name": "sale order",
                "partner_id": cls.partner.id,
                "user_id": cls.user.id,
            }
        )

        cls.order_line = cls.env["sale.order.line"].create(
            {
                "name": "order_line",
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
            }
        )

        cls.serial = cls.env["stock.production.lot"].create(
            {"name": "serial", "product_id": cls.product.id, 'company_id': cls.env.company.id}
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
    
    def test_reservation(self):
        self._confirm_sale_order()
        assert self.order_line.move_ids.reserved_availability == 1

    def test_no_reservation(self):
        self.env["ir.config_parameter"].set_param(
            "stock_auto_assign_disabled.config", "all"
        )
        self._confirm_sale_order()
        assert self.order_line.move_ids.reserved_availability == 0

    def _confirm_sale_order(self):
        self.sale_order.sudo(self.user).action_confirm()
