# Copyright 2024-today Numigi and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Move Origin Link",
    "version": "16.0.1.0.0",
    "category": "Stock",
    "description": "Add a link to the origin document from stock moves.",
    "summary": "Add a link to the origin document from stock moves.",
    "maintainer": "numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
    ],
    "assets": {
        "web.assets_backend": ["stock_move_origin_link/static/src/*"],
    },
}
