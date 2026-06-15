# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extend partner to add delivery contact fields."""

    _inherit = 'res.partner'

    is_delivery_contact = fields.Boolean(
        string='Is Delivery Contact',
        default=False,
        help='Check this box to mark this contact as a delivery contact. '
             'Delivery contacts can be selected to receive delivery notifications.',
    )
    delivery_contact_id = fields.Many2one(
        'res.partner',
        string='Delivery Contact',
        domain="[('parent_id', '=', id), ('is_delivery_contact', '=', True)]",
        help='Contact who will receive delivery notifications instead of the main partner. '
             'Only contacts with the "Is Delivery Contact" flag checked are available for selection.',
        check_company=True,
    )
