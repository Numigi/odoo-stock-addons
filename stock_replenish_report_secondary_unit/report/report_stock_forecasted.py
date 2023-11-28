# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.float_utils import float_round


class ReplenishmentReport(models.AbstractModel):
    _inherit = "report.stock.report_product_product_replenishment"

    def _get_report_data(self, product_template_ids=False, product_variant_ids=False):
        res = super()._get_report_data(product_template_ids, product_variant_ids)

        if product_template_ids:
            product_templates = self.env["product.template"].browse(
                product_template_ids
            )
            res["uom_second_unit"] = product_templates[:1].stock_secondary_uom_id.name
            res["product_obj"] = product_templates[:1]
            res[
                "virtual_available_second_unit"
            ] = self._get_virtual_available_second_unit(
                product_templates[:1],
                sum(product_templates.mapped("virtual_available")),
            )
        elif product_variant_ids:
            product_variants = self.env["product.product"].browse(product_variant_ids)
            res["uom_second_unit"] = product_variants[:1].stock_secondary_uom_id.name
            res["product_obj"] = product_variants[:1]
            res[
                "virtual_available_second_unit"
            ] = self._get_virtual_available_second_unit(
                product_variants[:1], sum(product_variants.mapped("virtual_available"))
            )
        return res

    def _prepare_report_line(
        self,
        quantity,
        move_out=None,
        move_in=None,
        replenishment_filled=True,
        product=False,
        reservation=False,
    ):
        res = super()._prepare_report_line(
            quantity,
            move_out,
            move_in,
            replenishment_filled,
            product,
            reservation,
        )
        product = product or (move_out.product_id if move_out else move_in.product_id)
        res["quantity_second_unit"] = self._get_secondary_unit_conversion(
            product=product, quantity=quantity
        )
        res["secondary_uom_id"] = product.stock_secondary_uom_id
        return res

    def _get_virtual_available_second_unit(self, product=False, virtual_available=0.0):
        return self._get_secondary_unit_conversion(product, virtual_available)

    def _get_secondary_unit_conversion(self, product=False, quantity=0.0):
        if not product.stock_secondary_uom_id:
            return 0.0
        else:
            qty = quantity / (product.stock_secondary_uom_id.factor or 1.0)
            val = float_round(qty, precision_rounding=product.uom_id.rounding)
            return val
