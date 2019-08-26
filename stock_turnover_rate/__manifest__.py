# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Turnover Rate",
    "summary": "Add turnover rate to products",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "queue_job",
    ],
    'data': [
        "data/ir_cron.xml",
        "views/config.xml",
        "views/product.xml",
        "views/product_category.xml",
        "views/product_template.xml",
    ],
    "installable": True,
}
