# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Tracking Reference",
    "version": "14.0.1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["delivery"],
    "summary": """Allow to enter the `Tracking reference` when the transfer
    status `out` or `int`  = `Done`.""",
    "data": [
        "views/delivery_view.xml",
    ],
    "installable": True,
}
