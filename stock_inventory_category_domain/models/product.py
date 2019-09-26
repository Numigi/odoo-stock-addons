# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', string='Company')
    available_in_inventory = fields.Boolean(string='Available in inventory')

    @api.constrains('company_id')
    def _check_product_company(self):
        """Check products of a category should have same company."""
        for category in self:
            if category.company_id:
                product_without_company = self.env['product.template'].search_count(
                    [('categ_id', '=', category.id), '|', ('company_id', '=', False),
                     ('company_id', '!=', category.company_id.id)])
                if product_without_company:
                    raise ValidationError(_(
                        'A products not related to a company are part of this category. products of a category on which a company is defined must be defined on the same company.'))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('company_id', 'categ_id')
    def _check_category_company(self):
        """Check products of a category have same company."""
        for product in self:
            if not product.company_id and product.categ_id.company_id:
                raise ValidationError(_(
                    'You can not associate category {category} for the product {product} because this category is related to the company {company} but this product is not related to a company.').format(
                    category=product.categ_id.name, product=product.name, company=product.categ_id.company_id.name))
