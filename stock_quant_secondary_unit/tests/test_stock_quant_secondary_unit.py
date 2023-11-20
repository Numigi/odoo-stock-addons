# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.addons.stock_secondary_unit.tests.test_stock_secondary_unit import (
    TestProductSecondaryUnit,
)


class TestCustomerReference(TestProductSecondaryUnit):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_stock_quant_secondary_unit_qty_available(self):
        # with the first factor 0.5
        self.assertEqual(self.quant_white.secondary_unit_qty_available, 20.0)
        self.assertEqual(
            self.quant_white.stock_secondary_uom_id,
            self.quant_white.product_id.stock_secondary_uom_id,
        )

    def test_stock_quant_stock_secondary_uom_id_changed(self):
        # Change the stock_secondary_uom_id to 0.9
        white_product = self.product_template.product_variant_ids[0]
        self.quant_white.product_tmpl_id.stock_secondary_uom_id = (
            white_product.secondary_uom_ids[1].id
        )
        self.assertEqual(white_product.secondary_uom_ids[1].factor, 0.9)
        white_product.refresh()
        self.quant_white.refresh()
        self.assertEqual(
            white_product.stock_secondary_uom_id,
            self.quant_white.stock_secondary_uom_id,
        )
        self.assertEqual(
            self.quant_white.stock_secondary_uom_id,
            white_product.secondary_uom_ids[1],
        )
        self.assertEqual(self.quant_white.stock_secondary_uom_id.factor, 0.9)
        self.assertEqual(self.quant_white.secondary_unit_qty_available, 11.11)
        self.assertEqual(self.quant_white.available_second_unit, 11.11)

    def test_fields_view_get_optional_show(self):
        res = self.env["stock.quant"].fields_view_get(
            view_id=self.env.ref("stock.view_stock_quant_tree_editable").id,
            view_type="tree",
        )
        eview = etree.fromstring(res["arch"])
        for field in res["fields"]:
            for node in eview.xpath("//field[@name='%s']" % field):
                self.assertEqual(
                    "show",
                    node.get("optional", "show"),
                )
