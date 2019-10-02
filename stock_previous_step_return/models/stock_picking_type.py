# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    enable_previous_step_return = fields.Boolean(
        help="Checking this box displays the `Return Products` button "
        "on the backorder confirmation wizard of a stock picking. "
        "When clicking on the button, a return picking is created "
        "with the undelivered products. "
        "This return picking allows to put the products back in stock."
    )

    enable_no_backorder = fields.Boolean(
        default=True,
        help="Checking this box displays the `No Backorder` button "
        "on the backorder confirmation wizard of a stock picking. ",
    )
