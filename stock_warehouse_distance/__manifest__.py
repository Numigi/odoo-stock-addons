# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Warehouse Distances",
    "summary": "Add distances between warehouses",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    'data': [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/stock_warehouse.xml",
        "views/stock_warehouse_distance.xml",
    ],
    "installable": True,
}
