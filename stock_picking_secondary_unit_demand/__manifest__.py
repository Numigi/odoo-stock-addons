# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Stock Picking Secondary Unit Demand",
    "version": "1.1.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "Stock",
    "summary": "Show the quantity ordered by the customer in the 2nd unit of measurement.",
    "depends": [
        "sale_order_secondary_unit",
        "stock_secondary_unit",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "installable": True,
}
