# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api
from odoo.tools.float_utils import float_round
from odoo.tools.misc import formatLang


class StockMove(models.Model):
    _inherit = "stock.move"

    merged_qty_uom_info = fields.Char(
        string="Request Secondary Unit",
        compute="_compute_merged_qty_uom_info",
        store=True,
    )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "sale_line_id",
        "sale_line_id.secondary_uom_qty",
        "sale_line_id.secondary_uom_id",
    )
    def _compute_merged_qty_uom_info(self):
        for line in self:
            if line.sale_line_id:
                secondary_uom_qty = line.sale_line_id.secondary_uom_qty
                secondary_uom_id = line.sale_line_id.secondary_uom_id
            else:
                secondary_uom_qty, secondary_uom_id = (
                    line._get_product_inventory_in_secondary_uom()
                )
            if secondary_uom_id:
                line.merged_qty_uom_info = "%s %s" % (
                    formatLang(
                        self.env,
                        secondary_uom_qty,
                    ),
                    secondary_uom_id.name,
                )

    def _get_product_inventory_in_secondary_uom(self):
        """
        Get a quantity to the secondary unit of measure.
        """
        self.ensure_one()
        stock_secondary_uom_id = self.product_id.stock_secondary_uom_id
        if not stock_secondary_uom_id:
            demand_qty = 0.0
        factor = self._get_factor_line()
        precision_rounding = (
            self.product_id.stock_secondary_uom_id.uom_id.rounding
            or self.product_uom.rounding or 0.01
        )
        demand_qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=precision_rounding,
        )
        return demand_qty, stock_secondary_uom_id
