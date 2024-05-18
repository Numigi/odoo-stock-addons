# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models
from odoo.tools.float_utils import float_round
from odoo.tools.misc import formatLang


class StockMove(models.Model):
    _inherit = "stock.move"

    merged_qty_uom_info = fields.Char(
        string="Request Secondary Unit",
        readonly=True,
        compute="_compute_merged_qty_uom_info",
    )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "sale_line_id.secondary_uom_qty",
        "sale_line_id.secondary_uom_id.name",
    )
    def _compute_merged_qty_uom_info(self):
        for line in self:
            line.merged_qty_uom_info = "%s %s" % (
                formatLang(
                    self.env,
                    line.sale_line_id.secondary_uom_qty
                    or line._get_product_inventory_in_secondary_uom(),
                ),
                line.sale_line_id.secondary_uom_id.name
                or line.product_id.stock_secondary_uom_id.name
                or "",
            )

    def _get_product_inventory_in_secondary_uom(self):
        """
        Get a quantity to the secondary unit of measure.
        """
        self.ensure_one()
        demand_qty = 0.0
        if self.product_id.stock_secondary_uom_id:
            demand_qty = self.product_uom_qty / (
                self.product_id.stock_secondary_uom_id.factor or 1.0
            )
            demand_qty = float_round(
                demand_qty, precision_rounding=self.product_uom.rounding
            )
        return demand_qty
