# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ProductCategory(models.Model):

    _inherit = "product.category"

    minimum_turnover_rate = fields.Float(digits=(16, 2))

    @api.constrains("minimum_turnover_rate", "target_turnover_rate")
    def _check_minimum_turnover_rate_not_greater_than_target(self):
        for category in self:
            min_rate = category.minimum_turnover_rate or 0
            target_rate = category.target_turnover_rate or 0
            greater_min_rate = float_compare(min_rate, target_rate, 2) == 1
            if greater_min_rate:
                raise ValidationError(
                    _(
                        "The minimum turnover rate for the product category {} "
                        "must be lower or equal to the target turnover rate."
                    ).format(category.display_name)
                )
