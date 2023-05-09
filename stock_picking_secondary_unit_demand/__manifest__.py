# © 2023 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': 'Stock Picking Secondary Unit Demand',
    'version': "1.0.0",
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'AGPL-3',
    'category': 'Stock',
    'summary': 'Show the quantity ordered by the customer in the 2nd unit of measurement.',
    'depends': [
        'sale_order_secondary_unit',
        'stock',
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
        "views/stock_move_line.xml",
    ],
    'installable': True,
}
