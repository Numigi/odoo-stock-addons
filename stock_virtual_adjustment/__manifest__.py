# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Virtual Adjustment",
    "version": "14.0.1.0.0",
    "summary": "Adjust the quantity of products in stock in the past.",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Stock",
    "depends": [
        "stock_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/stock_move.xml",
        "views/stock_virtual_adjustment.xml",
        "data/ir_sequence.xml",
    ],
    "installable": True,
}
