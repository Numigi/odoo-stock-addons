# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Production Lot RMA",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["rma_sale"],
    "summary": "Add the possibility to access the list of "
               "linked RMAs from the lot / serial number.",
    "data": [
        "views/stock_production_lot_views.xml",
    ],
    "installable": True,
}
