# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import AccessError
from .common import StockAccessCase


class TestInventoryAccess(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.inventory_1 = cls.env['stock.inventory'].create({
            'name': 'Inventory 1',
            'location_id': cls.location_1.id,
            'filter': 'product',
            'product_id': cls.product.id,
        })

        cls.inventory_2 = cls.env['stock.inventory'].create({
            'name': 'Inventory 2',
            'location_id': cls.location_2.id,
            'filter': 'product',
            'product_id': cls.product.id,
        })

        cls.inventory_1.action_start()
        cls.inventory_2.action_start()

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.inventory_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.inventory_2.sudo(self.user).check_extended_security_all()

    def _search_inventories(self):
        inventory_pool = self.env['stock.inventory'].sudo(self.user)
        domain = inventory_pool.get_extended_security_domain()
        return inventory_pool.search(domain)

    def test_search_domain_includes_authorized_inventory(self):
        assert self.inventory_1 in self._search_inventories()

    def test_search_domain_exludes_unauthorized_inventory(self):
        assert self.inventory_2 not in self._search_inventories()

    def test_if_all_warehouses_checked__no_inventory_excluded(self):
        self.user.all_warehouses = True
        inventories = self._search_inventories()
        assert self.inventory_1 in inventories
        assert self.inventory_2 in inventories


class TestInventoryLineAccess(TestInventoryAccess):
    """The behavior of inventory lines should be identical to inventories."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inventory_1 = cls.inventory_1.line_ids
        cls.inventory_2 = cls.inventory_2.line_ids

    def _search_inventories(self):
        inventory_pool = self.env['stock.inventory.line'].sudo(self.user)
        domain = inventory_pool.get_extended_security_domain()
        return inventory_pool.search(domain)
