# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Rental",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Inventory",
    "summary": "Add a logistic route for rental",
    "depends": ["stock"],
    "data": ["data/stock_location.xml", "views/stock_location.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
