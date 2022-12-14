# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Rental Conversion",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Allow to convert a salable product into a rentalable product",
    "depends": ["stock_serial_single_quant", "stock_rental"],
    "data": [
        "views/product_template.xml",
        "views/stock_production_lot.xml",
        "wizard/stock_rental_conversion_wizard.xml",
    ],
    "installable": True,
}
