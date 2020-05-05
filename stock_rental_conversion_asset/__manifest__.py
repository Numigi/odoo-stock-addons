# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Rental Conversion Asset",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Create an asset when converting a rental product",
    "depends": [
        "account_asset_management",
        "stock_rental_conversion",
        "stock_serial_asset",
        "onchange_helper",
    ],
    "data": ["views/product_template.xml", "wizard/stock_rental_conversion_wizard.xml"],
    "installable": True,
}
