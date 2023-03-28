# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Stock Move Description",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "category": "Stock",
    "summary": "Show description of each operation line on stock picking from purchase order.",
    "depends": ["purchase_stock"],
    "data": [
        "report/report_deliveryslip.xml",

        "views/stock_picking.xml",
    ],
    "installable": True,
}
