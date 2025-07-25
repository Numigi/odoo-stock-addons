# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Replenish Report Secondary Unit",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock_secondary_unit"],
    "summary": """Adds, in the inventory forecast report, the forecast quantities
    in the 2nd unit of measurement.""",
    "data": [
        "report/report_stock_forecasted.xml",
    ],
    "installable": True,
}
