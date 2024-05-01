# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Barcode",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Product",
    "summary": "Scan a barcode by picking",
    "depends": ["stock", "barcodes"],
    "data": [
        "data/picking_barcodes_data.xml",
        "views/stock_picking_view.xml",
        "views/stock_picking_type_view.xml",
    ],
    "installable": True,
    "application": False,
}
