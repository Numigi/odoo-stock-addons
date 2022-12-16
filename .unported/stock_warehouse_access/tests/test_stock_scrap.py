# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestScrapAccess(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.scrap_1 = cls.env['stock.scrap'].create({
            'name': 'Scrap 1',
            'location_id': cls.location_1.id,
            'product_id': cls.product.id,
            'product_uom_id': cls.product.uom_id.id,
        })

        cls.scrap_2 = cls.env['stock.scrap'].create({
            'name': 'Scrap 2',
            'location_id': cls.location_2.id,
            'product_id': cls.product.id,
            'product_uom_id': cls.product.uom_id.id,
        })

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.scrap_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.scrap_2.sudo(self.user).check_extended_security_all()

    def _search_inventories(self):
        scrap_pool = self.env['stock.scrap'].sudo(self.user)
        domain = scrap_pool.get_extended_security_domain()
        return scrap_pool.search(domain)

    def test_search_domain_includes_authorized_scrap(self):
        assert self.scrap_1 in self._search_inventories()

    def test_search_domain_exludes_unauthorized_scrap(self):
        assert self.scrap_2 not in self._search_inventories()

    def test_if_all_warehouses_checked__no_scrap_excluded(self):
        self.user.all_warehouses = True
        inventories = self._search_inventories()
        assert self.scrap_1 in inventories
        assert self.scrap_2 in inventories
