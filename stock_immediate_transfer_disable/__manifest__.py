# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Disable Immediate Transfer',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Warehouse',
    'summary': 'Disable Immediate Tranfer on Stock Pickings',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_type.xml',
        'wizard/stock_immediate_transfer.xml',
    ],
    'installable': True,
    'application': False,
}
