# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.stock.tests.common import TestStockCommon
from odoo.tests.common import Form


class TestStockImmediateTransferDisable(TestStockCommon):
    def setUp(self):
        super(TestStockImmediateTransferDisable, self).setUp()
        self.picking_out = self.PickingObj.create({
            'picking_type_id': self.picking_type_out,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location
        })
        self.move_a = self.MoveObj.create({
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 1,
            'product_uom': self.productA.uom_id.id,
            'picking_id': self.picking_out.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,

        })
        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        self.picking_type_out_id = self.env['stock.picking.type'].browse(
            self.picking_type_out)

    def test_stock_immediate_transfer_disable(self):
        self.picking_type_out_id.allow_imediate_transfer = False
        res_dict = self.picking_out.button_validate()
        self.assertEqual(res_dict.get('res_model'), 'stock.immediate.transfer')
        wizard = Form(self.env[res_dict['res_model']].with_context(
            res_dict['context'])).save()
        assert not wizard.allow_imediate_transfer

    def test_stock_immediate_transfer_enable(self):
        self.picking_type_out_id.allow_imediate_transfer = True
        res_dict = self.picking_out.button_validate()
        self.assertEqual(res_dict.get('res_model'), 'stock.immediate.transfer')
        wizard = Form(self.env[res_dict['res_model']].with_context(
            res_dict['context'])).save()
        assert wizard.allow_imediate_transfer
