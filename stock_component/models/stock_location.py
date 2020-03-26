# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def is_child_of(self, location):
        parent_location = self.location_id
        if parent_location == location:
            return True
        return (
            parent_location.is_child_of(location)
            if parent_location else False
        )
