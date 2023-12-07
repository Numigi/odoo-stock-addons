# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Split Quantity",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock"],
    "summary": """
        Split the quantities reserved on the outgoing transfer in 
        order to facilitate the packing operation.
    """,
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
}
