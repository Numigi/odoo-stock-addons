# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestStockPicking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "/", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "My Customer", "mandatory_delivery_order_signature": True}
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.move_lines.quantity_done = 1

    def test_no_signature_required(self):
        self.partner.mandatory_delivery_order_signature = False
        self._validate_picking()
        assert self.picking.state == "done"

    def test_signature_not_enabled_on_picking_type(self):
        self.warehouse.out_type_id.use_partner_signature = False
        self._validate_picking()
        assert self.picking.state == "done"

    def test_pending_signature(self):
        self.picking.pending_signature = True
        self._validate_picking()
        assert self.picking.state == "done"

    def test_missing_signature(self):
        with pytest.raises(ValidationError):
            self._validate_picking()

    @classmethod
    def _validate_picking(cls):
        cls.picking.action_done()

    def _test_task_digitized_signature(self):
        search_domain = [
            ("model", "=", "project.task"),
            ("res_id", "=", self.task.id),
            ("body", "like", "Signature has been created%"),
        ]
        # There is not messages created
        messages = self.env["mail.message"].search(search_domain)
        self.assertEqual(len(messages.ids), 0)
        # We add signature and write. Message must be created.
        self.task.customer_signature = (
            "R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =="
        )
        messages = self.env["mail.message"].search(search_domain)
        self.assertEqual(len(messages.ids), 1)
        # We create a new one. Message must be created.
        self.task = self.env["project.task"].create(
            {
                "name": "Task test #2",
                "customer_signature": "R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw ==",
            }
        )
        messages = self.env["mail.message"].search(search_domain)
        self.assertEqual(len(messages.ids), 1)
