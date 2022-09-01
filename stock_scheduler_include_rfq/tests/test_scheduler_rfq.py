# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests.common import SavepointCase


class TestSchedulerRFQ(SavepointCase):
    def test_scheduler_rfq(self):
        """
            - The product has a reordering rule
            - On the po generated, all rfq quantities are taking into
            account to calculate quantity_in_progress
        """
        self.warehouse_1 = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.id)], limit=1)

        # Create a supplier
        self.partner = self.env['res.partner'].create({
            'name': 'Smith'
        })

        # create reordering rule
        self.product = self.env['product.product'].create({
            'name': 'My Product',
            'type': 'product',
            'seller_ids': [(0, 0, {
                'name': self.partner.id,
                'price': 59.00,
                'min_qty': 1,
            })]
        })
    
        # create reordering rule
        self.orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': self.warehouse_1.id,
            'location_id': self.warehouse_1.lot_stock_id.id,
            'product_id': self.product.id,
            'product_min_qty': 100.000,
            'product_max_qty': 200.000,
        })
    
        # Create Delivery Order of 10 product
        self.purchase = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'date_planned': datetime.now(),
            'order_line': [(0, 0, {
                'name': self.product.display_name,
                'product_id': self.product.id,
                'product_qty': 50.0,
                'product_uom': self.product.uom_po_id.id,
                'price_unit': 59,
                'date_planned': datetime.now(),
            })],
        })

        # Run scheduler
        self.env['procurement.group'].run_scheduler()

        # Check sum purchase order line
        domain = [
            ('state', 'in', ('draft', 'sent', 'to approve')),
            ('product_id', '=', self.product.id),
            ('order_id.picking_type_id.warehouse_id', '=', self.warehouse_1.id)
        ]
        purchase_order_line = self.env['purchase.order.line'].search(domain)
        self.assertEqual(purchase_order_line.product_qty, 200)
