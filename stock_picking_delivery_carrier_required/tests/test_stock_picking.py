# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase, tagged


@tagged("-at_install", "post_install")
class TestStockPickingDelivery(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Only if stock_picking_delivery_carrier_required is installed on system
        if not cls.env['ir.module.module'].search(
            [
                ('name', '=', 'stock_picking_delivery_carrier_required'),
                ('state', '=', 'installed'),
            ],
            limit=1,
        ):
            cls.skipTest(
                cls, "Module stock_picking_delivery_carrier_required is not installed"
            )

        cls.product_delivery_normal = cls.env['product.product'].create(
            {
                'name': 'Normal Delivery Charges',
                'type': 'service',
                'list_price': 10.0,
                'categ_id': cls.env.ref('delivery.product_category_deliveries').id,
            }
        )
        cls.normal_delivery = cls.env['delivery.carrier'].create(
            {
                'name': 'Normal Delivery Charges',
                'fixed_price': 10,
                'delivery_type': 'fixed',
                'product_id': cls.product_delivery_normal.id,
            }
        )

    def test_shipping_info_required(self):
        # Check if carrier_id and carrier_tracking_ref are required
        delivery_form = Form(self.env["stock.picking"])
        delivery_form.picking_type_id = self.env.ref("stock.picking_type_out")
        delivery_form.location_id = self.env.ref("stock.stock_location_stock")
        delivery_form.location_dest_id = self.env.ref("stock.stock_location_customers")

        with self.assertRaises(AssertionError):
            delivery_form.save()

        delivery_form.carrier_id = self.normal_delivery
        delivery_form.carrier_tracking_ref = "123456"

        delivery_form.save()
