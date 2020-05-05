# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestWarehouse(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "My Company"})

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "My Warehouse", "code": "WH2", "company_id": cls.company.id}
        )

        cls.customer_location = cls.env.ref("stock_rental.customer_location")

    def test_rental_stock_location(self):
        assert self.warehouse.rental_location_id

    def test_rental_route(self):
        assert self.warehouse.rental_route_id

    def test_rental_picking_type(self):
        picking_type = self.warehouse.rental_type_id
        assert picking_type
        assert picking_type.code == "internal"
        assert picking_type.default_location_src_id == self.warehouse.rental_location_id
        assert picking_type.default_location_dest_id == self.customer_location

    def test_rental_return_picking_type(self):
        picking_type = self.warehouse.rental_return_type_id
        assert picking_type
        assert picking_type.code == "internal"
        assert picking_type.default_location_src_id == self.customer_location
        assert (
            picking_type.default_location_dest_id == self.warehouse.rental_location_id
        )

    def test_one_pull_from_rental_stock_to_client(self):
        pull = self.warehouse.rental_route_id.rule_ids.filtered(
            lambda r: r.action == "pull"
        )
        assert pull.location_src_id == self.warehouse.rental_location_id
        assert pull.location_id == self.customer_location
        assert pull.picking_type_id == self.warehouse.rental_type_id

    def test_one_push_from_client_to_rental_stock(self):
        pull = self.warehouse.rental_route_id.rule_ids.filtered(
            lambda r: r.action == "push"
        )
        assert pull.location_src_id == self.customer_location
        assert pull.location_id == self.warehouse.rental_location_id
        assert pull.picking_type_id == self.warehouse.rental_return_type_id

    def test_main_warehouse_has_rental_route(self):
        warehouse = self.env.ref("stock.warehouse0")
        assert warehouse.rental_route_id

    def test_main_warehouse_has_rental_picking_types(self):
        warehouse = self.env.ref("stock.warehouse0")
        assert warehouse.rental_type_id
        assert warehouse.rental_return_type_id
