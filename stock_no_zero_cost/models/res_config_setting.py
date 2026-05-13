# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_zero_cost_consumption = fields.Boolean(
        related='company_id.check_zero_cost_consumption', readonly=False)
    check_zero_cost_production = fields.Boolean(
        related='company_id.check_zero_cost_production', readonly=False)
    check_zero_cost_internal = fields.Boolean(
        related='company_id.check_zero_cost_internal', readonly=False)
