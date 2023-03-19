# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Disable Immediate Transfer",
    "version": "14.0.1.0.0",
    "author": "Savoir-faire Linux,Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Warehouse",
    "summary": "Disable Immediate Tranfer on Stock Pickings",
    "depends": ["stock"],
    "data": ["views/stock_picking_type.xml", "wizard/stock_immediate_transfer.xml"],
    "installable": True,
    "application": False,
}
