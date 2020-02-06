# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Inventory Line Domain',
    'version': '1.0.0',
    'summary': 'Restrain the selection of products on inventory lines.',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Stock',
    'depends': [
        'base_view_inheritance_extension',
        'stock',
    ],
    'data': [
        'views/stock_inventory.xml',
    ],
    'installable': True,
}
