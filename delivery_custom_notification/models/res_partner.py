# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Extend partner to add delivery contact type and field."""

    _inherit = 'res.partner'

    type = fields.Selection(
        selection_add=[('delivery_contact', 'Delivery Contact')],
        ondelete={'delivery_contact': 'set default'},
    )
    delivery_contact_id = fields.Many2one(
        'res.partner',
        string='Delivery Contact',
        domain="[('parent_id', '=', id), ('type', '=', 'delivery_contact')]",
        help='Contact who will receive delivery notifications instead of the main partner. '
             'Only contacts with type "Delivery Contact" are available for selection.',
        check_company=True,
    )
