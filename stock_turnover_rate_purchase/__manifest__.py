# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Turnover Rate / Purchase",
    "summary": "Display PO lines based on turnover rate",
    "version": "1.0.0",
    "category": "Purchase",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": ["purchase_stock", "stock_turnover_rate"],
    "data": [
        "views/product_category.xml",
        "views/product_template.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
