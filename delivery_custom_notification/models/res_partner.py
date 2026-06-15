# © 2026 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extend partner to add delivery contact field."""

    _inherit = 'res.partner'

    delivery_contact_id = fields.Many2one(
        'res.partner',
        string='Delivery Contact',
        help='Contact who will receive delivery notifications instead of the main partner.',
        check_company=True,
    )
