# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Orderpoint Scheduled Date",
    "summary": "Force Scheduled Date in Stock Orderpoint",
    "version": "14.0.1.2.1",
    "category": "stock",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_orderpoint_views.xml",
        "wizard/stock_warehouse_orderpoint_schedule_date.xml",
    ],
}
