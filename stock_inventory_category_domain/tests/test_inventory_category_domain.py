from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestStockInventoryCategoryDomain(TransactionCase):

    def setUp(self):
        """SetUp."""
        super(TestStockInventoryCategoryDomain, self).setUp()
        self.group_stock_manager = self.env.ref('stock.group_stock_manager')
        self.group_stock_user = self.env.ref('stock.group_stock_user')
        self.user_stock_manager = self.env['res.users'].create({
            'name': 'Stock Manager User',
            'login': 'manager',
            'email': 'sm@example.com',
            'groups_id': [(6, 0, [self.group_stock_manager.id])]
        })
        self.company = self.env.ref('stock.res_company_1')

    def test_check_category_company_for_product(self):
        # create product without company and category with company.
        product_abc = self.env['product.template'].sudo(self.user_stock_manager).create(
            {'name': 'ABC', 'company_id': False})
        category_super = self.env['product.category'].sudo(self.user_stock_manager).create(
            {'name': 'Super Category', 'company_id': self.company.id})
        # update product abc to set the company  to category_super should have message:
        # You can not associate category {category} for the product {product} because this category is related to the company {company} but this product is not related to a company.
        with self.assertRaises(ValidationError):
            product_abc.categ_id = category_super.id

    def test_check_product_company_for_category(self):
        # create two products without company and category without company.
        category = self.env['product.category'].sudo(self.user_stock_manager).create(
            {'name': 'Category', 'company_id': False})
        self.env['product.template'].sudo(self.user_stock_manager).create([
            {'name': 'Product 1', 'categ_id': category.id, 'company_id': False},
            {'name': 'Product 2', 'categ_id': category.id, 'company_id': False}
        ])
        # update category to set the company should have message:
        # A products not related to a company are part of this category. products of a category on which a company is defined must be defined on the same company.
        with self.assertRaises(ValidationError):
            category.company_id = self.company

    def test_available_category_in_inventory(self):
        # test category available in inventory
        # create two company (company_alpha,company_beta) and 3 categories
        company_alpha, company_beta = self.env['res.company'].sudo().create(
            [{'name': 'Company ALPHA'}, {'name': 'Company BETA'}])
        category1, category2, category3 = self.env['product.category'].sudo(self.user_stock_manager).create([
            {'name': 'Crème bains', 'company_id': company_alpha.id, 'available_in_inventory': True},
            {'name': 'Fourniture de bureau', 'company_id': False, 'available_in_inventory': True},
            {'name': 'Nourritures diverses', 'company_id': company_beta.id, 'available_in_inventory': True}
        ])
        # create two users (with group use User Stock) 1 have company Company ALPHA and user 2 have company BETA
        user1, user2 = self.env['res.users'].sudo().create([
            {'name': 'User 1', 'login': 'user1', 'email': 'user1@example.com', 'company_id': company_alpha.id,
             'company_ids': [(6, 0, [company_alpha.id])],
             'groups_id': [(6, 0, [self.group_stock_user.id])]},
            {'name': 'User 2', 'login': 'user2', 'email': 'user2@example.com', 'company_id': company_beta.id,
             'company_ids': [(6, 0, [company_beta.id])],
             'groups_id': [(6, 0, [self.group_stock_user.id])]}
        ])
        # search category by user 1 : should see only category1 and category2
        categ_domain = [('available_in_inventory', '=', True), '|', ('company_id', '=', company_alpha.id),
                        ('company_id', '=', False)]
        categs = self.env['product.category'].sudo(user1).search(categ_domain)
        self.assertEqual(set(categs.ids), set([category1.id, category2.id]))
        # search category by user 2 : should see only category3 and category2
        categ_domain = [('available_in_inventory', '=', True), '|', ('company_id', '=', company_beta.id),
                        ('company_id', '=', False)]
        categs = self.env['product.category'].sudo(user2).search(categ_domain)
        self.assertEqual(set(categs.ids), set([category3.id, category2.id]))
