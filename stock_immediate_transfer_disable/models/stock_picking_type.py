# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    allow_imediate_transfer = fields.Boolean(
        'Allow Immediate Transfer')
