# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Previous Step Return',
    'version': '11.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'summary': 'Return stock pickings of the previous step',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_type.xml',
        'wizard/stock_backorder_confirmation.xml',
    ],
    'installable': True,
}
