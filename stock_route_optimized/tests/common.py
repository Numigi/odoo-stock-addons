# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class StockRouteOptimizationCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "Company 2",
            }
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "WH2",
            })

        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.child_customer_location = cls.env["stock.location"].create(
            {
                "name": "Child Location",
                "location_id": cls.customer_location.id,
                "usage": "customer",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
            }
        )
        cls.route_delivery = cls.warehouse.delivery_route_id
        cls.rule_one_step_delivery = cls.route_delivery.rule_ids
        cls.procurement = cls.env["procurement.group"].create({
            "name": "S09999",
        })

    def setUp(self):
        super().setUp()
        self.values = {
            "warehouse_id": self.warehouse,
            "company_id": self.company,
        }
