# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Warehouse Access",
    "summary": "Restrict user access per warehouse",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "base_extended_security",
        "stock",
    ],
    'data': [
        "views/res_users.xml",
    ],
    "installable": True,
}
