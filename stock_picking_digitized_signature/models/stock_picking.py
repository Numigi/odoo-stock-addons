# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    partner_signature = fields.Binary(attachment=True, copy=False)
    pending_signature = fields.Boolean(copy=False, track_visibility="onchange")
    use_partner_signature = fields.Boolean(
        related="picking_type_id.use_partner_signature", string="Use Partner Signature"
    )

    @api.model
    def create(self, values):
        picking = super().create(values)
        if picking.partner_signature:
            values = {"partner_signature": picking.partner_signature}
            picking._track_signature(values, "partner_signature")
        return picking

    @api.multi
    def write(self, values):
        self._track_signature(values, "partner_signature")
        return super().write(values)

    def action_done(self):
        for picking in self:
            picking._check_partner_signature()
        return super().action_done()

    def _check_partner_signature(self):
        partner = self.partner_id.commercial_partner_id
        signature_required = (
            self.use_partner_signature
            and partner.mandatory_delivery_order_signature
            and not self.pending_signature
            and not self.partner_signature
        )
        if signature_required:
            raise ValidationError(
                _(
                    "You may not validate the transfer because the partner ({partner}) "
                    "requires the signature on delivery orders."
                    "\n\n"
                    "If the signature is pending, you may check this option in order "
                    "to validate the delivery order."
                ).format(partner=partner.display_name)
            )
