# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import StockInventoryCase


class TestProductSearchFilters(StockInventoryCase):

    def test_filter_products_by_category(self):
        products = self._search_products({
            'stock_inventory_product_category_filter': self.category_1.id})
        assert products == self.product_a | self.product_b

    def test_filter_unique_product(self):
        products = self._search_products({'stock_inventory_product_filter': self.product_a.id})
        assert products == self.product_a

    def test_filter_unique_lot(self):
        products = self._search_products({'stock_inventory_product_lot_filter': self.lot_b.id})
        assert products == self.product_b

    def _search_products(self, context):
        return self.env['product.product'].with_context(**context).search([])
