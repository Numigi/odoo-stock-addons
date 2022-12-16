# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestWarehouseAccess(StockAccessCase):

    def test_if_all_warehouses_checked__user_has_warehouse_access(self):
        self.user.all_warehouses = True
        assert self.user.has_warehouse_access(self.warehouse_2)

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.warehouse_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.warehouse_2.sudo(self.user).check_extended_security_all()

    def _search_warehouses(self):
        warehouse_pool = self.env['stock.warehouse'].sudo(self.user)
        domain = warehouse_pool.get_extended_security_domain()
        return warehouse_pool.search(domain)

    def test_search_domain_includes_authorized_warehouse(self):
        assert self.warehouse_1 in self._search_warehouses()

    def test_search_domain_exludes_unauthorized_warehouse(self):
        assert self.warehouse_2 not in self._search_warehouses()

    def test_if_all_warehouses_checked__no_warehouse_excluded(self):
        self.user.all_warehouses = True
        warehouses = self._search_warehouses()
        assert self.warehouse_1 in warehouses
        assert self.warehouse_2 in warehouses
