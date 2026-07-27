# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPicking(models.Model):
    """Extend stock picking to send custom delivery notifications."""

    _inherit = "stock.picking"

    def _send_confirmation_email(self):
        # Filter pickings that should receive custom notification
        custom_notification_pickings = self.filtered(
            lambda p: (
                p.picking_type_id.code == "outgoing"
                and p.carrier_id
                and p.carrier_id.send_delivery_notification
                and p.carrier_id.delivery_notification_template_id
                and p.partner_id
            )
        )

        # Send custom notifications
        for picking in custom_notification_pickings:
            # Determine recipient: delivery contact if set, otherwise main partner
            recipient = picking.partner_id.delivery_contact_id or picking.partner_id

            # Send email using the configured template and post to chatter for traceability
            # IMPORTANT: The email template should NOT have preconfigured recipients
            # (leave "To" and "Partner IDs" fields empty in template configuration)
            template = picking.carrier_id.delivery_notification_template_id
            picking.with_context(force_send=True).message_post_with_template(
                template.id,
                email_layout_xmlid="mail.mail_notification_light",
                partner_ids=recipient.ids,
            )

        # Call super for remaining pickings (standard behavior)
        remaining_pickings = self - custom_notification_pickings
        if remaining_pickings:
            super(StockPicking, remaining_pickings)._send_confirmation_email()
