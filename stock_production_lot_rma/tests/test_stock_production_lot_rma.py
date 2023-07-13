# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.rma.tests.test_rma import (
    TestRma,
)
from odoo.tests import Form


class TestStockProductionLotRma(TestRma):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.partner = cls.env['res.partner'].create(
            {'name': 'My Test Customer for RMA'})
        cls.pricelist_id = cls.env.ref('product.list0')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')

    def _create_delivery(self, lot_ids):
        so = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.pricelist_id.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'product_uom': self.product_uom_unit.id,
                'price_unit': 50.00,
            })],
        })
        so.action_confirm()
        action = so.picking_ids.button_validate()
        wizard = Form(self.env[action['res_model']].with_context(
            action['context'])).save()
        wizard.process()
        return so.picking_ids, so

    def _create_return(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        return_wizard = stock_return_picking_form.save()
        return_wizard.create_returns()

    def test_rma_on_lot_serial_number(self):
        # Change product tracking
        self.product.write(
            {"tracking": "lot"}
        )
        lot_1 = self.env['stock.production.lot'].create({
            'name': 'lot_consumed_1',
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.stock_location.id,
            'quantity': 100.0,
            'lot_id': lot_1.id,
            'reserved_quantity': 0.0,
        })
        # Create a return from a delivery picking
        picking, so = self._create_delivery(lot_1)
        self._create_return(picking)
        self.assertEqual(lot_1.rma_count, 1)

        # Then create a new sale and count RMA
        so_2 = so.copy()
        so_2.action_confirm()
        action = so_2.picking_ids.button_validate()
        wizard = Form(self.env[action['res_model']].with_context(
            action['context'])).save()
        wizard.process()
        self._create_return(so_2.picking_ids)
        self.assertEqual(lot_1.rma_count, 2)

        # Create RMA manually and count RMA
        rma = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma.action_confirm()
        rma.reception_move_id.quantity_done = 10
        rma.reception_move_id.picking_id.move_line_ids_without_package[0].lot_id = lot_1.id
        rma.reception_move_id.picking_id.button_validate()
        self.assertEqual(lot_1.rma_count, 3)
