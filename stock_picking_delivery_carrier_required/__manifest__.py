# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Delivery Carrier Required",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "stock",
    "depends": [
        "delivery",
    ],
    "summary": """
        Force users to systematically inform the 'Carrier' and the 'Tracking reference'
        about the delivery.
    """,
    "data": [
        "views/delivery_view.xml",
    ],
    "installable": True,
}
