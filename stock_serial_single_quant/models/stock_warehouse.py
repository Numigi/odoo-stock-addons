# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    bypass_serial_single_quant = fields.Boolean(
        string="Bypass Serial Constraints",
        default=False,
    )
