# © 2026 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    """Extend delivery carrier to add notification configuration."""

    _inherit = 'delivery.carrier'

    send_delivery_notification = fields.Boolean(
        string='Send Delivery Notification',
        default=False,
        help='When enabled, a custom notification email will be sent when deliveries using this carrier are validated.',
    )
    delivery_notification_template_id = fields.Many2one(
        'mail.template',
        string='Delivery Notification Template',
        domain="[('model', '=', 'stock.picking')]",
        help='Email template used for delivery notifications. Must be configured for stock.picking model.',
        check_company=True,
    )
