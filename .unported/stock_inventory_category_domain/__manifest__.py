# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Inventory Category Domain',
    'version': '12.0.1.0.0',
    'summary': 'Restriction the list of categories in inventory by company and option available in inventory.',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Stock',
    'depends': ['stock'],
    'data': [
        'views/product_views.xml',
        'views/inventory_views.xml',
    ],
    'installable': True,
}
