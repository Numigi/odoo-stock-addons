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
                product_without_company = self.env['product.template'].sudo().search_count([
                    ('categ_id', 'child_of', category.id),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '!=', category.company_id.id),
                ])
                if product_without_company:
                    raise ValidationError(_(
                        'Products not related to a company belong to this '
                        'category ({category}). '
                        'Products of a category on which a company is defined must be defined '
                        'on the same company.'
                    ).format(category.display_name))

    @api.constrains('company_id', 'parent_id', 'parent_id.company_id')
    def _check_parent_company(self):
        """Check that if the parent category has a company, the child category has the same."""
        for category in self:
            parent_company = category.parent_id.company_id
            category_company = category.company_id

            if parent_company and parent_company != category_company:
                raise ValidationError(_(
                    "The parent category {parent} belongs to the company {company}. "
                    "The child category {child} must belong to the same company."
                ).format(
                    parent=category.parent_id.display_name,
                    child=category.display_name,
                    company=parent_company.display_name,
                ))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('company_id', 'categ_id')
    def _check_category_company(self):
        """Check products of a category have same company."""
        for product in self:
            product_company = product.company_id.sudo()
            categ_company = product.categ_id.company_id.sudo()

            if not product_company and categ_company:
                raise ValidationError(_(
                    'You can not associate category {category} for the product {product} '
                    'because this category is related to the company {company} '
                    'but this product is not related to a company.').format(
                    category=product.categ_id.display_name,
                    product=product.display_name,
                    company=categ_company.display_name
                ))

            if product_company and categ_company and product_company != categ_company:
                raise ValidationError(_(
                    'You can not associate category {category} for the product {product} '
                    'because this category is related to the company {categ_company}. '
                    'This product is related to the company {product_company}.').format(
                    category=product.categ_id.display_name,
                    product=product.display_name,
                    categ_company=categ_company.display_name,
                    product_company=product_company.display_name,
                ))
