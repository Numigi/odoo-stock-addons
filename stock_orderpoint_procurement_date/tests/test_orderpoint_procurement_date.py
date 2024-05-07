# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta
from pytz import timezone, UTC
from odoo.tests import TransactionCase


class TestStockWarehouseOrderpoint(TransactionCase):

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()
        # Assuming that the product and company are set up in the test database
        self.orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.env.ref("product.product_product_1").id,
                "company_id": self.env.ref("base.main_company").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "product_min_qty": 0.0,
                "product_max_qty": 10.0,
                "qty_multiple": 1.0,
                "warehouse_id": self.env.ref("stock.warehouse0").id,
            }
        )

    def test__get_orderpoint_procurement_date_with_timezone(self):
        lead_days_date = datetime.now().date() + timedelta(days=5)
        expected_date = (
            timezone(self.orderpoint.company_id.partner_id.tz or "UTC")
            .localize(datetime.combine(lead_days_date, time(12)))
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        procurement_date = self.orderpoint._get_orderpoint_procurement_date(
            lead_days_date
        )
        self.assertEqual(procurement_date, expected_date)
