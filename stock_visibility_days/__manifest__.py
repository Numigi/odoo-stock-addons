# -*- coding: utf-8 -*-
{
    'name': "Stock Visibility Days (V14 Backport)",
    'summary': """
        Backport of the 'visibility_days' feature for reordering rules
        from Odoo 16 to V14.
    """,
    'description': """
        This module introduces the 'visibility_days' field on reordering rules
        (stock.warehouse.orderpoint).
        It allows considering the forecasted stock for a given number of days
        in the future when calculating the quantity to order.
        This helps in making more accurate replenishment decisions.
        It includes logic for standard stock, purchase, and manufacturing routes.
        A global 'Visibility Days' parameter is also added in the inventory settings.
    """,
    'author': "Your Name",
    'website': "https://www.numigi.com",
    'category': 'Inventory/Inventory',
    'version': '14.0.1.1.0',
    'depends': [
        'stock',
        'purchase_stock',
        'mrp',
    ],
    'data': [
        'views/stock_orderpoint_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
