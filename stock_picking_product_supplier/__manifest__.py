# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Product Supplier",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "stock",
    "depends": ["stock", "purchase"],
    "summary": """
        Adds the supplier reference of the product to stock move lines during receipt.
    """,
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
}
