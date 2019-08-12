# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class User(models.Model):

    _inherit = 'res.users'

    all_warehouses = fields.Boolean(default=True)
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'res_users_warehouse_rel',
        'user_id',
        'warehouse_id',
        string='Authorized Warehouses',
    )

    def has_warehouse_access(self, warehouse):
        """Return whether the user has access to the given warehouse."""
        return self.all_warehouses or warehouse in self.warehouse_ids

    def get_unauthorized_location_ids(self):
        all_warehouses = self.env['stock.warehouse'].sudo().search([])
        unauthorized_warehouses = all_warehouses - self.warehouse_ids
        unauthorized_view_locations = unauthorized_warehouses.mapped('view_location_id')
        unauthorized_locations = self.env['stock.location'].sudo().search(
            [('location_id', 'child_of', unauthorized_view_locations.ids)]
        )
        return unauthorized_locations.ids
