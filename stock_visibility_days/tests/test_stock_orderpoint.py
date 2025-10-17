# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase, tagged
from odoo import fields

@tagged('-at_install', 'post_install')
class TestStockWarehouseOrderpoint(TransactionCase):
    """Tests unitaires pour la classe StockWarehouseOrderpoint étendue."""

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()

        # Créer un produit simple
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'uom_id': self.ref('uom.product_uom_unit'),
            'uom_po_id': self.ref('uom.product_uom_unit'),
            'produce_delay': 3,  # délais fabrication fictif
        })

        # Créer un entrepôt et une localisation
        self.location = self.env.ref('stock.stock_location_stock')

        # Créer une règle d'achat fictive pour tester le "buy"
        self.route_buy = self.env.ref('purchase_stock.route_warehouse0_buy')
        self.rule_buy = self.route_buy.rule_ids[0]

        # Créer un orderpoint de base
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
    # Tests sur les champs calculés
    # ----------------------------------------------------------
    def test_compute_visibility_days_buy(self):
        """Vérifie que visibility_days prend la valeur de purchase_visibility_days pour une règle 'buy'."""
        self.orderpoint._compute_visibility_days()
        self.assertEqual(
            self.orderpoint.visibility_days,
            self.orderpoint.purchase_visibility_days,
            "La visibilité pour 'buy' n'est pas correctement calculée"
        )

    def test_set_visibility_days_buy(self):
        """Vérifie que le setter met bien à jour purchase_visibility_days."""
        self.orderpoint.visibility_days = 15.0
        self.orderpoint._set_visibility_days()
        self.assertEqual(
            self.orderpoint.purchase_visibility_days, 15.0,
            "Le setter n'a pas mis à jour purchase_visibility_days"
        )

    def test_compute_days_to_order_buy(self):
        """Vérifie que days_to_order prend bien le délai d'achat de la société."""
        self.orderpoint.company_id.days_to_purchase = 12
        self.orderpoint._compute_days_to_order()
        self.assertEqual(
            self.orderpoint.days_to_order,
            12,
            "days_to_order pour 'buy' n'est pas égal au délai d'achat"
        )

    def test_compute_lead_days(self):
        """Vérifie que lead_days_date est correctement calculée."""
        self.orderpoint._compute_lead_days()
        self.assertTrue(
            self.orderpoint.lead_days_date,
            "lead_days_date n'a pas été calculée"
        )

    # ----------------------------------------------------------
    # Tests sur la logique de calcul qty_to_order
    # ----------------------------------------------------------
    def test_compute_qty_to_order_below_min(self):
        """Si le stock prévisionnel est en dessous du min, la quantité doit être calculée."""
        self.orderpoint.qty_forecast = 0.0
        self.orderpoint._compute_qty_to_order()
        expected_qty = self.orderpoint.product_min_qty  # = 10
        # Comme le multiple est 5, et 10 est déjà un multiple, pas d'arrondi
        self.assertEqual(
            self.orderpoint.qty_to_order,
            expected_qty,
            "La quantité à commander n'est pas correcte quand stock < min"
        )

    def test_compute_qty_to_order_with_multiple(self):
        """Teste le cas où le calcul doit arrondir au multiple."""
        self.orderpoint.product_min_qty = 12
        self.orderpoint.product_max_qty = 12
        self.orderpoint.qty_forecast = 0
        self.orderpoint._compute_qty_to_order()
        # 12 arrondi au multiple de 5 => 15
        self.assertEqual(
            self.orderpoint.qty_to_order, 15.0,
            "La quantité à commander n'a pas été arrondie au multiple"
        )

    # ----------------------------------------------------------
    # Tests sur le contexte produit
    # ----------------------------------------------------------
    def test_get_product_context(self):
        """Vérifie que le contexte de visibilité contient bien la bonne date 'to_date'."""
        self.orderpoint._compute_lead_days()
        context = self.orderpoint._get_product_context(visibility_days=5)
        expected_to_date = datetime.combine(
            self.orderpoint.lead_days_date + relativedelta(days=5),
            time.max
        )
        self.assertEqual(context['location'], self.location.id)
        self.assertEqual(context['to_date'], expected_to_date)

    # ----------------------------------------------------------
    # Test de génération de procurement
    # ----------------------------------------------------------
    def test_get_procurements_generates_correct_line(self):
        """Vérifie que _get_procurements génère une procurement quand qty_to_order > 0."""
        self.orderpoint.qty_to_order = 10.0
        self.orderpoint._compute_lead_days()
        procurements = self.orderpoint._get_procurements(self.orderpoint)
        self.assertEqual(len(procurements), 1)
        procurement = procurements[0]
        self.assertEqual(procurement.product_id, self.product)
        self.assertEqual(procurement.product_qty, 10.0)
