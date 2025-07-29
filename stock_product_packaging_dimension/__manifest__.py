# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': 'Product Quant Package Dimension',
    'version': "1.0.0",
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://numigi.com/r/home',
    'license': 'AGPL-3',
    'category': 'Stock',
    'summary': """Add height, width and length to a stock quant package
    with its UOM for each field.""",
    'depends': [
        'delivery',
    ],
    'data': [
        'views/stock_quant_package.xml',
    ],
    'installable': True,
}
