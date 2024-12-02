# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Destination Width",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": [
        "stock",
    ],
    "summary": """
        Adjusts the width of the destination location field
        in the detailed operation wizard.
    """,
    "data": [
        "views/stock_move_views.xml",
    ],
    "installable": True,
}
