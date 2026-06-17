# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Delivery Custom Notification",
    "version": "14.0.1.2.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Inventory",
    "summary": "Send custom delivery notifications to specific contacts",
    "depends": [
        "delivery",
        "stock",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/delivery_carrier_views.xml",
    ],
    "installable": True,
}
