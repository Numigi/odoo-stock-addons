# -*- coding: utf-8 -*-
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestStockWarehouseOrderpoint(TransactionCase):
    """Unit tests for the extended StockWarehouseOrderpoint model."""

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()

        # Create a simple product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'uom_id': self.ref('uom.product_uom_unit'),
            'uom_po_id': self.ref('uom.product_uom_unit'),
            'produce_delay': 3,  # fictive manufacturing lead time
        })

        # Use the default stock location
        self.location = self.env.ref('stock.stock_location_stock')

        # Get a purchase route and one of its rules
        self.route_buy = self.env.ref('purchase_stock.route_warehouse0_buy')
        self.rule_buy = self.route_buy.rule_ids[0]

        # Create a basic orderpoint
        self.orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'name': 'Test Orderpoint',
            'product_id': self.product.id,
            'location_id': self.location.id,
            'product_min_qty': 10.0,
            'product_max_qty': 20.0,
            'qty_multiple': 5.0,
            'purchase_visibility_days': 7.0,
            'rule_ids': [(6, 0, [self.rule_buy.id])],
        })

    # ----------------------------------------------------------
    # Computed fields tests
    # ----------------------------------------------------------
    def test_compute_visibility_days_buy(self):
        """visibility_days should equal purchase_visibility_days for 'buy' rules."""
        self.orderpoint._compute_visibility_days()
        self.assertEqual(
            self.orderpoint.visibility_days,
            self.orderpoint.purchase_visibility_days,
            "visibility_days is not computed correctly for 'buy' action"
        )

    def test_set_visibility_days_buy(self):
        """Inverse method should update purchase_visibility_days when 'buy' route is used."""
        self.orderpoint.visibility_days = 15.0
        self.orderpoint._set_visibility_days()
        self.assertEqual(
            self.orderpoint.purchase_visibility_days, 15.0,
            "Inverse method did not update purchase_visibility_days"
        )

    def test_compute_days_to_order_buy(self):
        """days_to_order should match company.days_to_purchase for 'buy' rules."""
        self.orderpoint.company_id.days_to_purchase = 12
        self.orderpoint._compute_days_to_order()
        self.assertEqual(
            self.orderpoint.days_to_order,
            12,
            "days_to_order does not match company's purchase delay"
        )

    def test_compute_lead_days(self):
        """lead_days_date should be computed correctly."""
        self.orderpoint._compute_lead_days()
        self.assertTrue(
            self.orderpoint.lead_days_date,
            "lead_days_date was not computed"
        )

    # ----------------------------------------------------------
    # qty_to_order computation tests
    # ----------------------------------------------------------
    def test_compute_qty_to_order_below_min(self):
        """
        When forecasted qty is below min, the system should order up to max qty.
        In this case: max = 20, forecast = 0 → expected order = 20.
        """
        self.orderpoint.qty_forecast = 0.0
        self.orderpoint._compute_qty_to_order()
        expected_qty = self.orderpoint.product_max_qty  # = 20
        self.assertEqual(
            self.orderpoint.qty_to_order,
            expected_qty,
            "qty_to_order is not correct when forecast < min"
        )

    def test_compute_qty_to_order_with_multiple(self):
        """
        When min/max are not multiples, qty_to_order should be rounded up to the next multiple.
        Example: min = max = 12, multiple = 5 → order = 15.
        """
        self.orderpoint.product_min_qty = 12
        self.orderpoint.product_max_qty = 12
        self.orderpoint.qty_forecast = 0
        self.orderpoint._compute_qty_to_order()
        self.assertEqual(
            self.orderpoint.qty_to_order, 15.0,
            "qty_to_order was not rounded up to the next multiple"
        )

    # ----------------------------------------------------------
    # Product context tests
    # ----------------------------------------------------------
    def test_get_product_context(self):
        """_get_product_context should return correct location and future to_date."""
        self.orderpoint._compute_lead_days()
        context = self.orderpoint._get_product_context(visibility_days=5)
        expected_to_date = datetime.combine(
            self.orderpoint.lead_days_date + relativedelta(days=5),
            time.max
        )
        self.assertEqual(context['location'], self.location.id)
        self.assertEqual(context['to_date'], expected_to_date)

    # ----------------------------------------------------------
    # Procurement generation tests
    # ----------------------------------------------------------
    def test_get_procurements_generates_correct_line(self):
        """_get_procurements should generate one procurement if qty_to_order > 0."""
        self.orderpoint.qty_to_order = 10.0
        self.orderpoint._compute_lead_days()
        procurements = self.orderpoint._get_procurements(self.orderpoint)
        self.assertEqual(len(procurements), 1)
        procurement = procurements[0]
        self.assertEqual(procurement.product_id, self.product)
        self.assertEqual(procurement.product_qty, 10.0)
