# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        return super(ProcurementGroup,
                     self.with_context(procurement=True)
                     ).run(product_id, product_qty, product_uom,
                           location_id, name, origin, values)


