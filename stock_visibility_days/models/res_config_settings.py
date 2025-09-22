# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Add the global setting for visibility days
    stock_visibility_days = fields.Float(
        string="Global Visibility Days",
        config_parameter='stock.visibility_days',
        help="Global visibility days to apply to all reordering rules."
    )