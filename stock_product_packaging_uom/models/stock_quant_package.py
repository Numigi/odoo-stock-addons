# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, models


class StockQuantPackage(models.Model):
    """Spread dimension from package type"""

    _inherit = 'stock.quant.package'

    @api.onchange('packaging_id')
    def _onchange_packaging_id(self):
        if self.packaging_id:
            self.write({
                'height': self.packaging_id.height,
                'width': self.packaging_id.width,
                'packaging_length': self.packaging_id.packaging_length,
                'height_uom_id': self.packaging_id.height_uom_id,
                'width_uom_id': self.packaging_id.width_uom_id,
                'length_uom_id': self.packaging_id.length_uom_id,
            })
