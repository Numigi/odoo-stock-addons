# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Zero Cost Protection',
    'version': '14.0.1.0.2',
    'category': 'Inventory/Inventory',
    'summary': 'Prevent zero cost valuation on stock moves with a security bypass',
    "maintainer": "numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    'depends': [
        'stock',
        'stock_account',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'wizard/stock_zero_cost_wizard.xml',
    ],
    'installable': True,
    'application': False,
}

