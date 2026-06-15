# Delivery Custom Notification

## Overview

This module enables sending custom delivery notification emails to designated contacts when deliveries are validated. It provides fine-grained control over delivery notifications at the carrier level, with support for alternative email servers.

## Features

* **Delivery Contact Configuration**: Set a specific contact per partner who will receive delivery notifications
* **Carrier-Level Configuration**: Enable/disable custom notifications and configure email templates per delivery carrier
* **Intelligent Recipient Selection**: Automatically sends to delivery contact if configured, otherwise falls back to main partner
* **Template Flexibility**: Use custom email templates with support for alternative mail servers (e.g., Mailgun)
* **Selective Behavior**: Only affects outgoing deliveries (WH/OUT) with configured carriers
* **Preserves Standard Behavior**: Other deliveries continue using Odoo's standard confirmation emails

## Configuration

### Partner Configuration

1. Navigate to **Contacts** and open a partner form
2. Go to the **Sales & Purchase** tab
3. In the **Misc** section, set the **Delivery Contact** field
4. Select a contact from the partner's child contacts who should receive notifications

### Delivery Carrier Configuration

1. Navigate to **Inventory > Configuration > Delivery > Shipping Methods**
2. Open a delivery carrier form
3. Go to the new **Notifications** tab
4. Check **Send Delivery Notification**
5. Select a **Delivery Notification Template**
   - Template must be configured for the `stock.picking` model
   - You can create custom templates with tracking URLs and custom content
   - Templates can specify alternative mail servers

### Email Template Example (for 2Ship integration)

When creating your email template, you can include dynamic tracking URLs. For 2Ship integration:

```
Tracking URL: https://yourdomain.com/tracking-page?url=https%3A%2F%2Fship3.2ship.com%2FTracking%2FTrackClientTrackings%3FtrackingNumber%3D${object.carrier_tracking_ref}
```

Available fields in template:
* `${object.name}` - Delivery order number (e.g., WH/OUT/12245)
* `${object.origin}` - Source document (e.g., SO-89638)
* `${object.carrier_id.name}` - Carrier name
* `${object.carrier_tracking_ref}` - Tracking number
* `${object.partner_id.ref}` - Customer reference

**CRITICAL**: When creating the email template, **leave all recipient fields empty** (To, CC, Partner IDs). The module forces recipients programmatically to prevent duplicate emails.

## Usage

Once configured, the system automatically handles notification sending:

1. Create a delivery order for a partner with a configured delivery contact
2. Assign a carrier that has notifications enabled
3. Validate the delivery (set to "Done" status)
4. The system automatically sends the notification email to:
   - The configured delivery contact (if set), OR
   - The main partner (fallback)

## Technical Details

### Models Extended

* **res.partner**: Adds `delivery_contact_id` field
* **delivery.carrier**: Adds `send_delivery_notification` and `delivery_notification_template_id` fields
* **stock.picking**: Overrides `_send_confirmation_email()` method

### Business Logic

The module filters outgoing pickings where:
* `picking_type_id.code == 'outgoing'`
* `carrier_id.send_delivery_notification == True`
* `carrier_id.delivery_notification_template_id` is set
* `partner_id` exists

For these pickings, it sends custom notifications. All other pickings use standard Odoo behavior.

## Dependencies

* `delivery` - Core Odoo delivery module
* `stock` - Core Odoo inventory module

## Notes

* Only applies to outgoing delivery operations (Type: Delivery Orders)
* Does not affect other operation types (receipts, internal transfers, etc.)
* Compatible with third-party delivery integrations (e.g., delivery_2ship)
* Preserves standard notification behavior for non-configured carriers

## Support

For issues or feature requests, please contact your Odoo implementation partner.

## License

LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

## Credits

### Contributors

* Numigi

### Maintainer

This module is maintained by Numigi.
