# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockImmediateTransfer(models.TransientModel):

    _inherit = 'stock.immediate.transfer'

    allow_imediate_transfer = fields.Boolean(
        related='pick_id.picking_type_id.allow_imediate_transfer')
