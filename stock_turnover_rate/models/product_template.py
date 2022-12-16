# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    turnover_rate_active = fields.Boolean(
        related='product_variant_ids.turnover_rate_active',
        store=True,
        readonly=False,
    )
    turnover_rate = fields.Float(
        'Effective Turnover Rate',
        related='product_variant_ids.turnover_rate',
        store=True,
        readonly=True,
    )
    target_turnover_rate = fields.Float(
        related='categ_id.target_turnover_rate',
        store=True,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        template = super().create(vals)

        value = vals.get('turnover_rate_active')
        variants_to_update = template.product_variant_ids.filtered(
            lambda v: v.turnover_rate_active != value)
        variants_to_update.write({'turnover_rate_active': value})

        return template
