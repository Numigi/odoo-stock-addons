# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):

    _inherit = 'stock.warehouse'

    def distance_from(self, other_warehouse, raise_=True):
        """Compute the distance (km) between the warehouse and another warehouse.

        Optionaly, raises ValidationError if no distance found between the 2 warehouses.

        :ptype other: stock.warehouse
        :param raise_: whether to raise an exception if no distance found.
        :return: the distance if any found, None otherwise
        :rtype: Optional[float]
        """
        distances = self.env['stock.warehouse.distance'].search([
            '|',
            ('warehouse_1_id', '=', self.id),
            ('warehouse_2_id', '=', self.id),
        ])

        distance_from_other = next((
            d for d in distances
            if d.warehouse_1_id == other_warehouse or d.warehouse_2_id == other_warehouse
        ), None)

        if distance_from_other is None and raise_:
            raise ValidationError(_(
                'There is no defined distance between warehouses {warehouse_1} '
                'and {warehouse_2}.'
            ).format(
                warehouse_1=self.display_name,
                warehouse_2=other_warehouse.display_name,
            ))

        return None if distance_from_other is None else distance_from_other.distance
