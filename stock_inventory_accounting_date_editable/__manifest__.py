# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Inventory Accounting Date Editable',
    'version': '1.0.0',
    'summary': 'Make the accounting date editable on confirmed inventory adjustments',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Stock',
    'depends': [
        'base_view_inheritance_extension',
        'stock_account',
    ],
    'data': [
        'views/stock_inventory.xml',
    ],
    'installable': True,
}
