# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockWarehouseDistance(models.Model):

    _name = 'stock.warehouse.distance'
    _description = 'Warehouse Distance'

    warehouse_1_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse 1',
        ondelete='restrict',
        required=True,
    )
    warehouse_2_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse 2',
        ondelete='restrict',
        required=True,
    )
    distance = fields.Float(required=True)
    active = fields.Boolean(default=True)

    @api.constrains('warehouse_1_id', 'warehouse_2_id', 'active')
    def _check_no_duplicate_distances(self):
        for distance in self:
            dupplicate_distance = self.search([
                '|',
                '&',
                ('warehouse_1_id', '=', distance.warehouse_1_id.id),
                ('warehouse_2_id', '=', distance.warehouse_2_id.id),
                '&',
                ('warehouse_1_id', '=', distance.warehouse_2_id.id),
                ('warehouse_2_id', '=', distance.warehouse_1_id.id),
            ]) - distance

            if dupplicate_distance:
                raise ValidationError(_(
                    'A distance between {warehouse_1} and {warehouse_2} '
                    'already exists ({distance}). '
                    'You may not create 2 distances between the same warehouses.'
                ).format(
                    warehouse_1=distance.warehouse_1_id.display_name,
                    warehouse_2=distance.warehouse_2_id.display_name,
                    distance=dupplicate_distance[0].distance,
                ))

    @api.constrains('warehouse_1_id', 'warehouse_2_id')
    def _check_warehouses_1_and_2_are_different(self):
        for distance in self:
            if distance.warehouse_1_id == distance.warehouse_2_id:
                raise ValidationError(_(
                    'The warehouse defined in the field Warehouse 1 '
                    'must be different from the warehouse defined '
                    'in Warehouse 2.'
                ))
