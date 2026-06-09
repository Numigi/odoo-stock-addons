# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# pylint: disable=pointless-statement
# noqa: B018

{
    "name": "Stock Serial Single Quant",
    "summary": "Add constraints on serial numbers",
    "version": "14.0.1.1.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_production_lot.xml",
        "views/stock_warehouse.xml",
    ],
    "installable": True,
}
