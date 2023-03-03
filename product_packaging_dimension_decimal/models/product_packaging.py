# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ProductPackaging(models.Model):
    """Change integer field to float."""

    _inherit = "product.packaging"

    def _get_uom_domain(self):
        uom_ids = []
        uom_ids.extend(
            (
                self.env.ref("uom.product_uom_foot").id,
                self.env.ref("uom.product_uom_meter").id,
            )
        )
        return [("id", "in", uom_ids)]

    def _get_default_uom(self):
        return self.env.ref("uom.product_uom_meter")

    height = fields.Float("Height")
    width = fields.Float("Width")
    packaging_length = fields.Float("Length")
    height_uom_id = fields.Many2one(
        "uom.uom",
        string="Height UOM",
        domain=_get_uom_domain,
        default=_get_default_uom
    )
    width_uom_id = fields.Many2one(
        "uom.uom",
        string="Width UOM",
        domain=_get_uom_domain,
        default=_get_default_uom
    )
    length_uom_id = fields.Many2one(
        "uom.uom",
        string="Length UOM",
        domain=_get_uom_domain,
        default=_get_default_uom
    )

