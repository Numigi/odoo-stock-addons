# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestStockPickingTypeAccess(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_1 = cls.warehouse_1.in_type_id
        cls.picking_type_2 = cls.warehouse_2.in_type_id
        cls.dropship_type = cls.env.ref('stock_dropshipping.picking_type_dropship')

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.picking_type_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.picking_type_2.sudo(self.user).check_extended_security_all()

    def test_if_picking_type_unbound_to_warehouse__access_error_not_raised(self):
        self.dropship_type.sudo(self.user).check_extended_security_all()

    def _search_picking_types(self):
        picking_type_pool = self.env['stock.picking.type'].sudo(self.user)
        domain = picking_type_pool.get_extended_security_domain()
        return picking_type_pool.search(domain)

    def test_search_domain_includes_authorized_picking_type(self):
        assert self.picking_type_1 in self._search_picking_types()

    def test_search_domain_exludes_unauthorized_picking_type(self):
        assert self.picking_type_2 not in self._search_picking_types()

    def test_if_all_warehouses_checked__no_picking_type_excluded(self):
        self.user.all_warehouses = True
        picking_types = self._search_picking_types()
        assert self.picking_type_1 in picking_types
        assert self.picking_type_2 in picking_types

    def test_search_domain_includes_picking_type_unbound_to_warehouse(self):
        assert self.dropship_type in self._search_picking_types()
