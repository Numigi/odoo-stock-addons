# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models

MAPPING_FIELD_CACHE = {
    "height": "h_cache",
    "width": "w_cache",
    "packaging_length": "pl_cache",
}


class ProductPackaging(models.Model):
    """Change integer field to float."""

    _inherit = "product.packaging"

    @api.model
    def init(self):
        """
        Init method to set the field cache value to the right field value.
        It will be triggered when this module is installed or updated (directly or
        via its dependency).
        """
        all_product_pack = self.search([])
        for product_pack in all_product_pack:
            for field, field_cache in MAPPING_FIELD_CACHE.items():
                setattr(product_pack, field, getattr(product_pack, field_cache))
        super(ProductPackaging, self).init()

    def _get_uom_domain(self):
        uom_ids = []
        uom_ids.extend(
            (
                self.env.ref("uom.product_uom_foot").id,
                self.env.ref("uom.product_uom_meter").id,
                self.env.ref("uom.product_uom_inch").id,
                self.env.ref("uom.product_uom_cm").id,
            )
        )
        return [("id", "in", uom_ids)]

    def _get_default_uom(self):
        return self.env.ref("uom.product_uom_meter")

    height = fields.Float("Height")
    width = fields.Float("Width")
    packaging_length = fields.Float("Length")
    height_uom_id = fields.Many2one(
        "uom.uom", string="Height UOM", domain=_get_uom_domain, default=_get_default_uom
    )
    width_uom_id = fields.Many2one(
        "uom.uom", string="Width UOM", domain=_get_uom_domain, default=_get_default_uom
    )
    length_uom_id = fields.Many2one(
        "uom.uom", string="Length UOM", domain=_get_uom_domain, default=_get_default_uom
    )

    # We only need these fields for module update.
    # Especially in case of updating the module `delivery`
    # to avoid any conflict with the original fields.
    # Original field is integer, so after updating the module `delivery`,
    # we lose all value because odoo is converting all field to integer (in delivery)
    # then float (in this module that depend on it).
    # So we need to restore the right value from the field cache.
    # Name of the fields are different to avoid any conflict with the original fields.
    h_cache = fields.Float("Height Cache")
    w_cache = fields.Float("Width Cache")
    pl_cache = fields.Float("Length Cache")

    def update_cache_field_values(self, values):
        for key, new_key in MAPPING_FIELD_CACHE.items():
            if key in values:
                values[new_key] = values[key]
        return values

    @api.model
    def create(self, value):
        value = self.update_cache_field_values(value)
        return super().create(value)

    def write(self, vals):
        vals = self.update_cache_field_values(vals)
        return super().write(vals)
