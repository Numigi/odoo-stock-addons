# © 2026 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Delivery Custom Notification',
    'version': '14.0.1.1.0',
    'category': 'Inventory/Delivery',
    'summary': 'Send custom delivery notifications to specific contacts',
    'description': """
Delivery Custom Notification
=============================
This module allows sending specific delivery notification emails to designated
delivery contacts, configured at the delivery carrier level.

Key Features
------------
* Tag contacts as "Delivery Contacts" with a dedicated boolean field
* Configure a delivery contact per partner who will receive notifications
* Configure custom email template per delivery carrier
* Automatic email sending when outgoing delivery is validated
* Override standard Odoo delivery confirmation for specific carriers
* Support for alternative email servers (e.g., Mailgun) via template configuration
* Search and filter delivery contacts easily

Configuration
-------------
1. On contact records, check "Is Delivery Contact" to tag them (Sales & Purchase section)
2. On partner form, select a tagged delivery contact (Sales & Purchase tab)
3. On delivery carrier form, enable "Send Delivery Notification" (Notifications tab)
4. Select an email template for the notification
5. The system will automatically send emails to the configured contact when deliveries are done
    """,
    'author': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'depends': [
        'delivery',
        'stock',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/delivery_carrier_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
