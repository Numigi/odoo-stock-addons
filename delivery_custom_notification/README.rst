Delivery Custom Notification
============================
This module enables sending custom delivery notification emails to designated contacts when deliveries are validated.

It provides fine-grained control over delivery notifications at the carrier level, with support for alternative email servers.

Features
--------
* **Contact Typing**: Use native Odoo contact types with new "Delivery Contact" option
* **Filtered Selection**: Only contacts with type "Delivery Contact" appear in the selection dropdown
* **Easy Search**: Filter and find all delivery contacts via the search view
* **Carrier-Level Configuration**: Enable/disable custom notifications and configure email templates per delivery carrier
* **Intelligent Recipient Selection**: Automatically sends to delivery contact if configured, otherwise falls back to main partner
* **Template Flexibility**: Use custom email templates with support for alternative mail servers (e.g., Mailgun)
* **Chatter Traceability**: All sent emails appear in the delivery order's message history
* **Selective Behavior**: Only affects outgoing deliveries (WH/OUT) with configured carriers
* **Preserves Standard Behavior**: Other deliveries continue using Odoo's standard confirmation emails

Configuration
-------------

Step 1: Create Delivery Contact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Navigate to **Contacts** and open a partner/company form
2. Create a new contact (or open an existing child contact)
3. In the contact form, set the **Type** field to **"Delivery Contact"**
4. Fill in the contact's email address
5. Save the contact

**Note**: The "Delivery Contact" type appears in the standard Odoo Type field (same as Invoice Address, Delivery Address, etc.).

Step 2: Assign Delivery Contact to Partner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Navigate to **Contacts** and open a partner/company form
2. Go to the **Sales & Purchase** tab
3. In the **Misc** section, set the **Delivery Contact** field
4. The dropdown will only show child contacts with type "Delivery Contact"
5. You can create a new delivery contact on-the-fly by clicking "Create and Edit"

**Tip**: Use the search filter "Delivery Contacts" to quickly find all contacts of this type in your system.

Step 3: Configure Email Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Before configuring carriers, create your delivery notification email template:

1. Navigate to **Settings > Technical > Email > Email Templates**
2. Create a new template with these settings:

   - **Name**: e.g., "Delivery Notification - 2Ship"
   - **Applies to**: ``stock.picking`` (Transfers)
   - **Email From**: Configure if using alternative server (e.g., Mailgun)
   - **Outgoing Mail Server**: Select alternative server if needed
   - **⚠️ CRITICAL - Leave EMPTY**:

     - "To (Emails)" field
     - "To (Partners)" field
     - "CC" field

   - **Subject**: Your custom subject line
   - **Body**: Your custom HTML/text content

**Why leave recipients empty?**

- The module programmatically sets the recipient (delivery contact or partner)
- This prevents duplicate emails if template has preconfigured recipients
- This ensures emails appear in the delivery order's Chatter (message history)
- Operations teams can see email sending history directly on the picking

Step 4: Configure Delivery Carrier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Navigate to **Inventory > Configuration > Delivery > Shipping Methods**
2. Open a delivery carrier form
3. Go to the new **Notifications** tab
4. Check **Send Delivery Notification**
5. Select your **Delivery Notification Template** (created in Step 3)

Email Template Example (2Ship Integration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When creating your email template, you can include dynamic tracking URLs. For 2Ship integration::

    Tracking URL: https://yourdomain.com/tracking-page?url=https%3A%2F%2Fship3.2ship.com%2FTracking%2FTrackClientTrackings%3FtrackingNumber%3D${object.carrier_tracking_ref}

Available fields in template:

* ``${object.name}`` - Delivery order number (e.g., WH/OUT/12245)
* ``${object.origin}`` - Source document (e.g., SO-89638)
* ``${object.carrier_id.name}`` - Carrier name
* ``${object.carrier_tracking_ref}`` - Tracking number
* ``${object.partner_id.ref}`` - Customer reference

Usage
-----
Once configured, the system automatically handles notification sending:

1. Create a delivery order for a partner with a configured delivery contact
2. Assign a carrier that has notifications enabled
3. Validate the delivery (set to "Done" status)
4. The system automatically sends the notification email to:

   - The configured delivery contact (if set), OR
   - The main partner (fallback)

5. **Email Traceability**: The sent email appears in the delivery order's Chatter (message history at the bottom of the form), allowing operations teams to verify the notification was sent and to whom

Technical Details
-----------------

Models Extended
~~~~~~~~~~~~~~~
* **res.partner**: Extends ``type`` selection with new "Delivery Contact" option and adds ``delivery_contact_id`` field
* **delivery.carrier**: Adds ``send_delivery_notification`` and ``delivery_notification_template_id`` fields
* **stock.picking**: Overrides ``_send_confirmation_email()`` method

Business Logic
~~~~~~~~~~~~~~
The module filters outgoing pickings where:

* ``picking_type_id.code == 'outgoing'``
* ``carrier_id.send_delivery_notification == True``
* ``carrier_id.delivery_notification_template_id`` is set
* ``partner_id`` exists

For these pickings, it sends custom notifications. All other pickings use standard Odoo behavior.

Multi-Company Support
~~~~~~~~~~~~~~~~~~~~~
The module includes ``check_company=True`` on relational fields to ensure data consistency in multi-company environments.

Integration with Third-Party Carriers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is fully compatible with third-party delivery integrations such as ``delivery_2ship``. The tracking number (``carrier_tracking_ref``) is automatically populated by the carrier integration and can be used in email templates.

Contributors
------------
The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.
