# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Main Module',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Install all addons required for testing.',
    'depends': [
        'sale',  # Required to test stock_return_from_next_step

        'stock_immediate_transfer_disable',
        'stock_move_list_cost',
        'stock_move_origin_link',
        'stock_picking_show_address',
        'stock_return_from_next_step',
    ],
    'installable': True,
}
