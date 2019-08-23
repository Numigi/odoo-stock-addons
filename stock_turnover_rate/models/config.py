# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

DEFAULT_TURNOVER_DAYS = 365
TURNOVER_DAYS_PARAMETER_NAME = 'stock_turnover_days'


def get_stock_turnover_days(env) -> int:
    value = env['ir.config_parameter'].get_param(TURNOVER_DAYS_PARAMETER_NAME)
    return int(value) if value else DEFAULT_TURNOVER_DAYS


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    stock_turnover_days = fields.Integer(
        config_parameter=TURNOVER_DAYS_PARAMETER_NAME,
        default=DEFAULT_TURNOVER_DAYS,
    )
