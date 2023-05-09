# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models
from odoo.tools.misc import formatLang


class StockMove(models.Model):
    _inherit = "stock.move"

    merged_qty_uom_info = fields.Char(
        string="Request Secondary Unit", readonly=True,
        compute="_compute_merged_qty_uom_info"
    )

    @api.depends("sale_line_id.secondary_uom_qty", "sale_line_id.secondary_uom_id.name")
    def _compute_merged_qty_uom_info(self):
        for line in self:
            line.merged_qty_uom_info = "%s %s" % (
                formatLang(
                    self.env, line.sale_line_id.secondary_uom_qty),
                line.sale_line_id.secondary_uom_id.name or ''
            )
