# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductSupplierName(TransactionCase):
    def setUp(self):
        super(TestProductSupplierName, self).setUp()
        self.product = self.browse_ref("product.product_product_3")
        self.partner = self.env.ref("base.res_partner_2")
        self.supplier = self.env.ref("base.res_partner_2")
        self.product.write(
            {
                "seller_ids": [
                    (0, 0, {"name": self.supplier.id, "product_code": "SLL_CODE"})
                ],
            }
        )

    def test_product_supplier_name_with_supplier(self):
        picking = self.env["stock.picking"].create({
            "partner_id": self.partner.id,
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "location_id": self.env.ref("stock.stock_location_suppliers").id,
            "location_dest_id": self.env.ref("stock.stock_location_stock").id,
        })
        move_line = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.assertEqual(move_line.product_supplier_name, self.supplier.name)

    def test_product_supplier_name_without_supplier(self):
        self.product.write({"seller_ids": [(5, 0, 0)]})
        picking = self.env["stock.picking"].create({
            "partner_id": self.partner.id,
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "location_id": self.env.ref("stock.stock_location_suppliers").id,
            "location_dest_id": self.env.ref("stock.stock_location_stock").id,
        })
        move_line = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom_id": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.assertFalse(move_line.product_supplier_name)
