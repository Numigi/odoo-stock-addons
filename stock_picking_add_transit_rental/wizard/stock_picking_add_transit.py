# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPickingAddTransit(models.TransientModel):

    _inherit = "stock.picking.add.transit"

    def _should_add_transit_before(self):
        """Manage the case of a rental return picking.

        When adding a transit to a rental return,
        the transit must be added after the existing picking.

        The behavior is the same as for a recipt or a delivery return.
        """
        is_rental_return = self.picking_id.location_id.is_rental_customer_location
        if is_rental_return:
            return False

        return super()._should_add_transit_before()
