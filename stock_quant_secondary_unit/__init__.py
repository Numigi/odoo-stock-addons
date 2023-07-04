# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from odoo import api, SUPERUSER_ID


def _update_secondary_unit_qty_available(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    quant_lines = env['stock.quant'].search([])
    quant_lines.with_context(
        inventory_mode=True).compute_secondary_unit_qty_available()
