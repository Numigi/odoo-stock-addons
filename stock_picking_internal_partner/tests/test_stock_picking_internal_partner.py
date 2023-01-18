# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestPickingInternalPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.transit_1 = cls.env["stock.location"].create(
            {
                "name": "Transit 1",
                "usage": "transit",
                "location_id": cls.warehouse.view_location_id.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
        })
        cls.order_line_values = {
            'product_id': cls.product_a.id,
            'name': cls.product_a.name,
            'product_uom_qty': 1,
        }
        cls.user = cls.env['res.users'].create({
            'name': 'test@example.com',
            'email': 'test@example.com',
            'login': 'test@example.com',
        })
        cls.partner = cls.user.partner_id
        cls.order_1 = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'warehouse_id': cls.warehouse.id,
            'order_line': [
                (0, 0, cls.order_line_values.copy()),
                (0, 0, cls.order_line_values.copy()),
            ],
        })

    def test_stock_picking_internal_partner(self):
        picking = self.env['stock.picking']
        picking_values = {
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_id': self.env.ref(
                'stock.stock_location_suppliers').id,
            'location_dest_id': self.transit_1.id,
        }
        internal_picking = picking.create(picking_values)
        self.assertEquals(internal_picking.partner_id.id,
                          self.warehouse.partner_id.id)
