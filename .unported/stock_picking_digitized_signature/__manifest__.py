# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Digitized Signature",
    "version": "1.0.0",
    "author": "Numigi",
    "website": "https://numigi.com",
    "category": "Inventory",
    "license": "AGPL-3",
    "depends": ["web_widget_digitized_signature", "stock"],
    "data": [
        "views/res_partner.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
