# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Internal Partner",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "summary": "Set Warehouse Address In Internal Transfer",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml"
    ],
    "installable": True,
    "post_init_hook": 'set_warehouse_as_partner'
}