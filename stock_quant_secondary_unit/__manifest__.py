# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Secondary Unit",
    "version": "1.0.3",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock_secondary_unit"],
    "summary": "Add 2nd unit and 2nd Unit On Hand Qty on some stock quant views.",
    "data": [
        "views/stock_quant.xml",
    ],
    "post_init_hook": "_update_secondary_unit_qty_available",
    "installable": True,
}
