# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    is_rental_customer_location = fields.Boolean(
        help="Check this box if this location is used for products "
        "rented to a customer."
    )
    
    is_rental_stock_location = fields.Boolean(
        help="Check this box if this location is used for products "
        "rented to a location."
    )
