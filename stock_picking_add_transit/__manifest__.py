# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Add Transit",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "summary": "Allow to add a transit to a stock picking",
    "depends": ["stock", "stock_dropshipping"],
    "data": [
        "views/stock_picking.xml",
        "wizard/stock_picking_add_transit.xml"
    ],
    "installable": True,
}
