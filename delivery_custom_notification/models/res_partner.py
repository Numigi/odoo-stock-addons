# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extend partner to add delivery contact field and reverse relation."""

    _inherit = 'res.partner'

    delivery_contact_id = fields.Many2one(
        'res.partner',
        string='Delivery Contact',
        help='Contact who will receive delivery notifications instead of the main partner. '
             'Any partner can be selected as the delivery contact.',
        check_company=True,
    )
    delivery_contact_for_partner_ids = fields.One2many(
        'res.partner',
        'delivery_contact_id',
        string='Is Delivery Contact For',
        help='Partners that use this contact as their delivery contact.',
    )
