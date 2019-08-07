# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class StockMoveAccessCase(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.move_1_in = cls._create_stock_move({
            'name': 'Move 1 In',
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.warehouse_1.lot_stock_id.id,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
        })
        cls.move_1_out = cls._create_stock_move({
            'name': 'Move 1 Out',
            'location_id': cls.warehouse_1.lot_stock_id.id,
            'location_dest_id': cls.customer_location.id,
            'picking_type_id': cls.warehouse_1.out_type_id.id,
        })

        cls.move_2_in = cls._create_stock_move({
            'name': 'Move 2 In',
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.warehouse_2.lot_stock_id.id,
            'picking_type_id': cls.warehouse_2.in_type_id.id,
        })
        cls.move_2_out = cls._create_stock_move({
            'name': 'Move 2 Out',
            'location_id': cls.warehouse_2.lot_stock_id.id,
            'location_dest_id': cls.customer_location.id,
            'picking_type_id': cls.warehouse_2.out_type_id.id,
        })

        cls.dropship_type = cls.env.ref('stock_dropshipping.picking_type_dropship')
        cls.dropship_move = cls._create_stock_move({
            'name': 'Dropship Move',
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.customer_location.id,
            'picking_type_id': cls.dropship_type.id,
        })

        moves = (
            cls.move_1_in |
            cls.move_1_out |
            cls.move_2_in |
            cls.move_2_out |
            cls.dropship_move
        )
        moves._action_confirm()
        moves._action_assign()

        for move in moves:
            move.move_line_ids.qty_done = 1
            move.picking_id.put_in_pack()

    @classmethod
    def _create_stock_move(cls, custom_vals):
        vals = {
            'product_uom_qty': 1,
            'product_id': cls.product.id,
            'product_uom': cls.product.uom_id.id,
        }
        vals.update(custom_vals)
        return cls.env['stock.move'].create(vals)


class TestStockMoveAccess(StockMoveAccessCase):

    def _search_moves(self):
        domain = self.env['stock.move'].sudo(self.user).get_extended_security_domain()
        return self.env['stock.move'].search(domain)

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.move_1_in.sudo(self.user).check_extended_security_all()
        self.move_1_out.sudo(self.user).check_extended_security_all()

    def test_if_not_has_origin_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.move_2_in.sudo(self.user).check_extended_security_all()

    def test_if_not_has_destination_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.move_2_out.sudo(self.user).check_extended_security_all()

    def test_if_move_unbound_to_warehouse__access_error_not_raised(self):
        self.dropship_move.sudo(self.user).check_extended_security_all()

    def test_search_domain_includes_authorized_move(self):
        moves = self._search_moves()
        assert self.move_1_in in moves
        assert self.move_1_out in moves

    def test_search_domain_exludes_unauthorized_move(self):
        moves = self._search_moves()
        assert self.move_2_in not in moves
        assert self.move_2_out not in moves

    def test_if_all_warehouses_checked__no_move_excluded(self):
        self.user.all_warehouses = True
        moves = self._search_moves()
        assert self.move_1_in in moves
        assert self.move_1_out in moves
        assert self.move_2_in in moves
        assert self.move_2_out in moves

    def test_search_domain_includes_location_unbound_to_warehouse(self):
        assert self.dropship_move in self._search_moves()


class TestStockMoveLineAccess(TestStockMoveAccess):
    """The behavior with stock move lines should be identical to stock moves."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_1_in = cls.move_1_in.move_line_ids
        cls.move_1_out = cls.move_1_out.move_line_ids
        cls.move_2_in = cls.move_2_in.move_line_ids
        cls.move_2_out = cls.move_2_out.move_line_ids
        cls.dropship_move = cls.dropship_move.move_line_ids

    def _search_moves(self):
        domain = self.env['stock.move.line'].sudo(self.user).get_extended_security_domain()
        return self.env['stock.move.line'].search(domain)


class TestStockPickingAccess(TestStockMoveAccess):
    """The behavior with stock picking should be identical to stock moves."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_1_in = cls.move_1_in.picking_id
        cls.move_1_out = cls.move_1_out.picking_id
        cls.move_2_in = cls.move_2_in.picking_id
        cls.move_2_out = cls.move_2_out.picking_id
        cls.dropship_move = cls.dropship_move.picking_id

    def _search_moves(self):
        domain = self.env['stock.picking'].sudo(self.user).get_extended_security_domain()
        return self.env['stock.picking'].search(domain)
