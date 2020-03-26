# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Component",
    "summary": "Define components on serial numbers",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/stock_production_lot.xml",
    ],
    "installable": True,
}
