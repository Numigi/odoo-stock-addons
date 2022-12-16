# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockReturnCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 1", "code": "WH1-TEST"}
        )
        cls.warehouse.delivery_steps = "pick_ship"

        cls.ship_type = cls.warehouse.out_type_id
        cls.ship_type.enable_previous_step_return = True

        cls.stock_user = cls.env["res.users"].create(
            {
                "name": "Stock User",
                "login": "test_stock_user",
                "email": "test_stock_user@test.com",
                "groups_id": [(4, cls.env.ref("stock.group_stock_user").id)],
            }
        )

        cls.product_a = cls.env["product.product"].create(
            {"name": "My Product", "type": "product"}
        )

        cls.product_b = cls.env["product.product"].create(
            {"name": "My Product B", "type": "product"}
        )

        for product in (cls.product_a, cls.product_b):
            cls.env["stock.quant"].create(
                {
                    "location_id": cls.warehouse.lot_stock_id.id,
                    "product_id": product.id,
                    "quantity": 100,
                }
            )

        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "customer": True}
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "name": cls.product_a.display_name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 20,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_b.id,
                            "name": cls.product_b.display_name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 20,
                        },
                    ),
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.delivery = cls.sale_order.picking_ids.filtered(
            lambda p: p.picking_type_id == cls.ship_type
        )
        cls.pick = cls.sale_order.picking_ids - cls.delivery

    @classmethod
    def select_quantities(cls, picking, product, quantity, lot=None):
        move = picking.move_lines.filtered(lambda m: m.product_id == product)
        if lot:
            line = move.move_line_ids.filtered(
                lambda l: not l.lot_id or l.lot_id == lot
            )
            if line:
                line.lot_id = lot
            else:
                line = cls.env["stock.move.line"].create(
                    {
                        "picking_id": picking.id,
                        "move_id": move.id,
                        "location_dest_id": move.location_dest_id.id,
                        "location_id": move.location_id.id,
                        "lot_id": lot.id,
                        "product_id": product.id,
                        "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                    }
                )
        else:
            line = move.move_line_ids.filtered(lambda l: not l.lot_id)

        line.qty_done = quantity

    @classmethod
    def return_products(cls):
        wizard_action = cls.delivery.button_validate()
        wizard = cls.env["stock.backorder.confirmation"].browse(wizard_action["res_id"])
        wizard.button_return_products()

    @classmethod
    def get_return_picking(cls):
        return cls.sale_order.picking_ids.filtered(
            lambda p: p.location_dest_id == cls.warehouse.lot_stock_id
        )


class TestStockReturn(StockReturnCase):
    """Test the case where all products are processed on the first step."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.process_pick_step()

    @classmethod
    def process_pick_step(cls):
        cls.select_quantities(cls.pick, cls.product_a, 20)
        cls.select_quantities(cls.pick, cls.product_b, 20)
        cls.pick.action_done()

        assert cls.pick.state == "done"
        assert cls.delivery.state == "assigned"

    def test_if_one_product_processed__return_picking_has_one_line(self):
        self.select_quantities(self.delivery, self.product_a, 20)
        self.return_products()
        picking = self.get_return_picking()
        assert len(picking.move_lines) == 1
        assert picking.move_lines.product_id == self.product_b

    def test_delivery_backorder_is_cancelled(self):
        self.select_quantities(self.delivery, self.product_a, 20)
        self.return_products()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", self.delivery.id)]
        )
        assert backorder.state == "cancel"

    def test_if_one_product_partially_processed__return_picking_has_two_lines(self):
        self.select_quantities(self.delivery, self.product_a, 19)
        self.return_products()
        picking = self.get_return_picking()
        assert len(picking.move_lines) == 2

    def test_if_returned_quantity_is_set_properly(self):
        self.select_quantities(self.delivery, self.product_a, 20)
        self.select_quantities(self.delivery, self.product_b, 6)
        self.return_products()
        picking = self.get_return_picking()
        assert picking.move_lines.product_uom_qty == 14  # 20 - 6

    def test_after_return__delivery_is_processed(self):
        delivered_quantity = 6
        self.select_quantities(self.delivery, self.product_a, delivered_quantity)
        self.return_products()
        assert self.delivery.state == "done"
        assert self.delivery.move_lines.product_id == self.product_a
        assert self.delivery.move_lines.product_uom_qty == delivered_quantity


class TestBackOrderOnFirstStep(StockReturnCase):
    """Test the case where the first step is completed with a backorder."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.process_pick_step()
        cls.prepare_ship_step()
        cls.return_products()

    @classmethod
    def process_pick_step(cls):
        cls.select_quantities(cls.pick, cls.product_a, 10)
        cls.select_quantities(cls.pick, cls.product_b, 10)

        wizard_action = cls.pick.button_validate()
        wizard = cls.env["stock.backorder.confirmation"].browse(wizard_action["res_id"])
        wizard.process()

        cls.backorder = cls.env["stock.picking"].search(
            [("backorder_id", "=", cls.pick.id)]
        )
        cls.select_quantities(cls.backorder, cls.product_a, 10)
        cls.select_quantities(cls.backorder, cls.product_b, 10)
        cls.backorder.action_done()

        assert cls.pick.state == "done"
        assert cls.backorder.state == "done"
        assert cls.delivery.state == "assigned"

    @classmethod
    def prepare_ship_step(cls):
        cls.delivered_quantity_a = 8
        cls.delivered_quantity_b = 9
        cls.select_quantities(cls.delivery, cls.product_a, cls.delivered_quantity_a)
        cls.select_quantities(cls.delivery, cls.product_b, cls.delivered_quantity_b)

    def test_after_return__delivery_is_processed(self):
        assert self.delivery.state == "done"

    def test_after_return__selected_quantities_delivered(self):
        line_a = self.delivery.move_lines.filtered(
            lambda l: l.product_id == self.product_a
        )
        assert line_a.product_uom_qty == self.delivered_quantity_a

        line_b = self.delivery.move_lines.filtered(
            lambda l: l.product_id == self.product_b
        )
        assert line_b.product_uom_qty == self.delivered_quantity_b

    def test_return_picking_has_one_move_per_pick_step_move(self):
        return_picking = self.get_return_picking()
        assert (
            len(return_picking.move_lines) == 4
        )  # 4 returned moves because 4 linked origin moves

    def test_return_picking_is_assigned(self):
        """Test that the returned picking is at the assigned state.

        This means that all stock move lines are reserved.
        """
        return_picking = self.get_return_picking()
        assert return_picking.state == "assigned"


class TestProductionLots(StockReturnCase):
    """Test the case where the first step is completed with a backorder with production lots."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.process_pick_step()
        cls.prepare_ship_step()
        cls.return_products()

    @classmethod
    def process_pick_step(cls):
        cls.lot_1 = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_a.id, "name": "00000001"}
        )
        cls.lot_2 = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_a.id, "name": "00000002"}
        )

        cls.select_quantities(cls.pick, cls.product_a, 0)
        cls.select_quantities(cls.pick, cls.product_a, 5, lot=cls.lot_1)
        cls.select_quantities(cls.pick, cls.product_a, 5, lot=cls.lot_2)
        cls.select_quantities(cls.pick, cls.product_b, 20)

        wizard_action = cls.pick.button_validate()
        wizard = cls.env["stock.backorder.confirmation"].browse(wizard_action["res_id"])
        wizard.process()

        backorder = cls.env["stock.picking"].search(
            [("backorder_id", "=", cls.pick.id)]
        )
        cls.select_quantities(backorder, cls.product_a, 5, lot=cls.lot_1)
        cls.select_quantities(backorder, cls.product_a, 5, lot=cls.lot_2)
        backorder.action_done()

        assert cls.pick.state == "done"
        assert backorder.state == "done"
        assert cls.delivery.state == "assigned"

    @classmethod
    def prepare_ship_step(cls):
        cls.delivered_quantity_1 = 3
        cls.delivered_quantity_2 = 4
        cls.delivered_quantity_a = 7  # 3 + 4
        cls.expected_returned_qty = 13  # 20 - 3 - 4
        cls.delivered_quantity_b = 20
        cls.select_quantities(
            cls.delivery, cls.product_a, cls.delivered_quantity_1, lot=cls.lot_1
        )
        cls.select_quantities(
            cls.delivery, cls.product_a, cls.delivered_quantity_2, lot=cls.lot_2
        )
        cls.select_quantities(cls.delivery, cls.product_b, cls.delivered_quantity_b)

    def test_after_return__delivery_is_processed(self):
        assert self.delivery.state == "done"

    def test_after_return__selected_quantities_delivered(self):
        line_1 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.lot_1)
        assert line_1.product_id == self.product_a
        assert line_1.qty_done == self.delivered_quantity_1

        line_2 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.lot_2)
        assert line_2.product_id == self.product_a
        assert line_2.qty_done == self.delivered_quantity_2

        line_b = self.delivery.move_lines.filtered(
            lambda l: l.product_id == self.product_a
        )
        assert line_b.product_uom_qty == self.delivered_quantity_a

        line_b = self.delivery.move_lines.filtered(
            lambda l: l.product_id == self.product_b
        )
        assert line_b.product_uom_qty == self.delivered_quantity_b

    def test_return_picking_has_remaining_undelivered_quantities(self):
        return_picking = self.get_return_picking()
        move_lines = return_picking.move_line_ids
        assert sum(move_lines.mapped("product_uom_qty")) == self.expected_returned_qty

    def test_return_picking_is_assigned(self):
        """Test that the returned picking is at the assigned state.

        This means that all stock move lines are reserved.
        """
        return_picking = self.get_return_picking()
        assert return_picking.state == "assigned"
