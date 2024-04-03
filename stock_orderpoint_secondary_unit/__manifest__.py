# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Orderpoint Secondary Unit",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": [
        "stock_secondary_unit",
    ],
    "summary": """ 
        Use secondary unit on order and group 
        replenishment lines by primary unit of measure.
    """,
    "data": [
        "views/stock_warehouse_orderpoint_views.xml",
    ],
    "installable": True,
}
