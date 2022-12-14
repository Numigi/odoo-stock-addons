# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
import pytest
from odoo.exceptions import AccessError
from odoo.addons.stock_warehouse_access.tests.common import StockAccessCase


class PurchaseOrderAccessCase(StockAccessCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({'name': 'Supplier', 'supplier': True})

        cls.picking_type_1 = cls.warehouse_1.in_type_id
        cls.picking_type_2 = cls.warehouse_2.in_type_id
        cls.dropship_type = cls.env.ref('stock_dropshipping.picking_type_dropship')

        cls.order_1 = cls._create_purchase_order(cls.picking_type_1)
        cls.order_2 = cls._create_purchase_order(cls.picking_type_2)
        cls.dropship_order = cls._create_purchase_order(cls.dropship_type)

    @classmethod
    def _create_purchase_order(cls, picking_type):
        return cls.env['purchase.order'].create({
            'partner_id': cls.supplier.id,
            'picking_type_id': picking_type.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'name': cls.product.name,
                'product_qty': 1,
                'product_uom': cls.product.uom_po_id.id,
                'price_unit': 10,
                'date_planned': datetime.now(),
            })]
        })


class TestPurchaseOrderAccess(PurchaseOrderAccessCase):

    def test_if_has_warehouse_access__access_error_not_raised(self):
        self.order_1.sudo(self.user).check_extended_security_all()

    def test_if_not_has_warehouse_access__access_error_raised(self):
        with pytest.raises(AccessError):
            self.order_2.sudo(self.user).check_extended_security_all()

    def test_if_order_unbound_to_warehouse__access_error_not_raised(self):
        self.dropship_type.sudo(self.user).check_extended_security_all()

    def _search_orders(self):
        order_pool = self.env['purchase.order'].sudo(self.user)
        domain = order_pool.get_extended_security_domain()
        return order_pool.search(domain)

    def test_search_domain_includes_authorized_order(self):
        assert self.order_1 in self._search_orders()

    def test_search_domain_exludes_unauthorized_order(self):
        assert self.order_2 not in self._search_orders()

    def test_if_all_warehouses_checked__no_order_excluded(self):
        self.user.all_warehouses = True
        orders = self._search_orders()
        assert self.order_1 in orders
        assert self.order_2 in orders

    def test_search_domain_includes_order_unbound_to_warehouse(self):
        assert self.dropship_order in self._search_orders()


class TestPurchaseOrderLineAccess(TestPurchaseOrderAccess):
    """Access to purchase order lines should be the same as purchase orders."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_1 = cls.order_1.order_line
        cls.order_2 = cls.order_2.order_line
        cls.dropship_order = cls.dropship_order.order_line

    def _search_orders(self):
        order_pool = self.env['purchase.order.line'].sudo(self.user)
        domain = order_pool.get_extended_security_domain()
        return order_pool.search(domain)
