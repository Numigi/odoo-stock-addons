# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductCategory(models.Model):

    _inherit = 'product.category'

    target_turnover_rate = fields.Float(
        digits=(16, 2),
    )
