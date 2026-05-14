# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    check_zero_cost_consumption = fields.Boolean(
        string="Check Zero Cost on Consumption", default=False)
    check_zero_cost_production = fields.Boolean(
        string="Check Zero Cost on Production", default=False)
    check_zero_cost_internal = fields.Boolean(
        string="Check Zero Cost on Internal Transfers", default=False)

    zero_cost_precision_id = fields.Many2one(
        comodel_name="decimal.precision",
        string="Zero Cost Precision",
        help="Determine the number of decimal places used to consider a product cost as zero.",
        default=lambda self: self.env.ref("product.decimal_price", raise_if_not_found=False),
    )
    zero_qty_precision_id = fields.Many2one(
        comodel_name="decimal.precision",
        string="Quantity Precision",
        help="Determine the number of decimal places used to consider "
             "a product quantity as zero.",
        default=lambda self: self.env.ref("product.decimal_product_uom",
                                          raise_if_not_found=False),
    )

    def _get_zero_cost_precision_digits(self):
        """
        Retrieve the decimal precision digits configured for the current company.
        Fallback to the standard 'Product Price' precision if none is configured.
        """
        self.ensure_one()
        precision_record = self.sudo().zero_cost_precision_id
        precision_name = precision_record.name if precision_record else "Product Price"
        return self.env["decimal.precision"].precision_get(precision_name)

    def _get_zero_qty_precision_digits(self):
        self.ensure_one()
        precision_record = self.sudo().zero_qty_precision_id
        precision_name = precision_record.name if precision_record \
            else "Product Unit of Measure"
        return self.env["decimal.precision"].precision_get(precision_name)
