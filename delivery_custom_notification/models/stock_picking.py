# © 2026 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPicking(models.Model):
    """Extend stock picking to send custom delivery notifications."""

    _inherit = 'stock.picking'

    def _send_confirmation_email(self):
        """
        Override to send custom delivery notifications based on carrier configuration.

        This method filters outgoing pickings with custom notification enabled and sends
        emails to the configured delivery contact (or main partner as fallback).
        Other pickings use the standard confirmation email behavior.
        """
        # Filter pickings that should receive custom notification
        custom_notification_pickings = self.filtered(
            lambda p: p.picking_type_id.code == 'outgoing' and
                     p.carrier_id and
                     p.carrier_id.send_delivery_notification and
                     p.carrier_id.delivery_notification_template_id and
                     p.partner_id
        )

        # Send custom notifications
        for picking in custom_notification_pickings:
            # Determine recipient: delivery contact if set, otherwise main partner
            recipient = picking.partner_id.delivery_contact_id or picking.partner_id

            # Send email using the configured template
            # Using send_mail() with email_values to force recipient and override any
            # recipients configured in the template itself (avoids duplicate recipients)
            template = picking.carrier_id.delivery_notification_template_id
            template.send_mail(
                picking.id,
                force_send=True,
                email_values={
                    'recipient_ids': [(6, 0, recipient.ids)],
                },
                notif_layout='mail.mail_notification_light',
            )

        # Call super for remaining pickings (standard behavior)
        remaining_pickings = self - custom_notification_pickings
        if remaining_pickings:
            super(StockPicking, remaining_pickings)._send_confirmation_email()
