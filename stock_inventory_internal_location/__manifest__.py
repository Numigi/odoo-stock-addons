# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Warehouse Internal Location",
    "summary": "Prevent selecting non-internal (stock) locations in inventories.",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    'data': [
        "views/stock_inventory.xml",
    ],
    "installable": True,
}
