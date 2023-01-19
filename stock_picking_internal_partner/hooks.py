# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def set_warehouse_as_partner(cr, registry):
    """ Set warehouse as partner config in Internal Transfers"""
    _logger.info('Start Set warehouse as partner config in Internal Transfers')
    env = api.Environment(cr, SUPERUSER_ID, {})
    model = env['stock.picking.type']
    internal_transfers = model.search([('code', '=', 'internal')])
    internal_transfers.sudo().write({'warehouse_as_partner': True})
    _logger.info('Set warehouse as partner config in Internal Transfers')
