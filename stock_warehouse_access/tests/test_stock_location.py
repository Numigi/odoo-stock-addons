# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestLocationAccess(StockAccessCase):

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.location_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.location_2.sudo(self.user).check_extended_security_all()

    def test_if_location_unbound_to_warehouse__access_error_not_raised(self):
        self.supplier_location.sudo(self.user).check_extended_security_all()

    def _search_locations(self):
        location_pool = self.env['stock.location'].sudo(self.user)
        domain = location_pool.get_extended_security_domain()
        return location_pool.search(domain)

    def test_search_domain_includes_authorized_location(self):
        assert self.location_1 in self._search_locations()

    def test_search_domain_exludes_unauthorized_location(self):
        assert self.location_2 not in self._search_locations()

    def test_if_all_warehouses_checked__no_location_excluded(self):
        self.user.all_warehouses = True
        locations = self._search_locations()
        assert self.location_1 in locations
        assert self.location_2 in locations

    def test_search_domain_includes_location_unbound_to_warehouse(self):
        assert self.supplier_location in self._search_locations()
