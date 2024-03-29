# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Secondary Unit",
    "version": "1.0.4",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock_secondary_unit"],
    "summary": "Add 2nd unit quantities to stock quants",
    "data": [
        "views/stock_quant.xml",
    ],
    "post_init_hook": "_update_secondary_unit_qty",
    "installable": True,
}
