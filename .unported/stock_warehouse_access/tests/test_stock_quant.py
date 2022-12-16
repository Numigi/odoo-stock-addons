# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestStockQuantAccess(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.quant_1 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'quantity': 1,
            'location_id': cls.location_1.id,
        })

        cls.quant_2 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'quantity': 1,
            'location_id': cls.location_2.id,
        })

        cls.supplier_quant = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'quantity': 1,
            'location_id': cls.supplier_location.id,
        })

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.quant_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.quant_2.sudo(self.user).check_extended_security_all()

    def test_if_quant_unbound_to_warehouse__access_error_not_raised(self):
        self.supplier_quant.sudo(self.user).check_extended_security_all()

    def _search_quants(self):
        quant_pool = self.env['stock.quant'].sudo(self.user)
        domain = quant_pool.get_extended_security_domain()
        return quant_pool.search(domain)

    def test_search_domain_includes_authorized_quant(self):
        assert self.quant_1 in self._search_quants()

    def test_search_domain_exludes_unauthorized_quant(self):
        assert self.quant_2 not in self._search_quants()

    def test_if_all_warehouses_checked__no_quant_excluded(self):
        self.user.all_warehouses = True
        quants = self._search_quants()
        assert self.quant_1 in quants
        assert self.quant_2 in quants

    def test_search_domain_includes_quant_unbound_to_warehouse(self):
        assert self.supplier_quant in self._search_quants()


class TestStockQuantPackageAccess(TestStockQuantAccess):
    """The behavior with packages should be identical as quants."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.quant_1 = cls.env['stock.quant.package'].create({
            'quant_ids': [(4, cls.quant_1.id)],
        })

        cls.quant_2 = cls.env['stock.quant.package'].create({
            'quant_ids': [(4, cls.quant_2.id)],
        })

        cls.supplier_quant = cls.env['stock.quant.package'].create({
            'quant_ids': [(4, cls.supplier_quant.id)],
        })

    def _search_quants(self):
        quant_pool = self.env['stock.quant.package'].sudo(self.user)
        domain = quant_pool.get_extended_security_domain()
        return quant_pool.search(domain)
