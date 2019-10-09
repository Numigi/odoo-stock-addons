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
        self.company_2 = self.env['res.company'].create({'name': 'Company 2'})

    def _create_category(self, company=None, parent=None):
        return self.env['product.category'].sudo(self.user_stock_manager).create({
            'name': 'Super Category',
            'company_id': company.id if company else None,
            'parent_id': parent.id if parent else None,
        })

    def _create_product(self, company=None, category=None):
        vals = {
            'name': 'Super Product',
            'company_id': company.id if company else None,
        }
        if category:
            vals['categ_id'] = category.id
        return self.env['product.product'].sudo(self.user_stock_manager).create(vals)

    def test_check_category_company_for_product(self):
        category_super = self._create_category(company=self.company)
        product_abc = self._create_product()

        with self.assertRaises(ValidationError):
            product_abc.categ_id = category_super

    def test_on_change_company_on_category__category_company_must_be_the_same(self):
        product_abc = self._create_product(company=self.company)
        category_super = self._create_category(company=self.company_2)

        with self.assertRaises(ValidationError):
            product_abc.categ_id = category_super

    def test_parent_category_company_must_be_the_same(self):
        parent_category = self._create_category(company=self.company_2)

        with self.assertRaises(ValidationError):
            self._create_category(parent=parent_category)

    def test_on_change_company_on_category__products_company_can_not_be_empty(self):
        category = self._create_category()
        self._create_product(category=category)
        self._create_product(category=category)

        with self.assertRaises(ValidationError):
            category.company_id = self.company

    def test_on_change_company_on_category__products_must_have_same_company(self):
        category = self._create_category()
        self._create_product(category=category, company=self.company)
        self._create_product(category=category, company=self.company)

        with self.assertRaises(ValidationError):
            category.company_id = self.company_2

    def test_on_change_company_on_parent_category__products_must_have_same_company(self):
        parent_category = self._create_category()
        category = self._create_category(parent=parent_category)
        self._create_product(category=category, company=self.company)
        self._create_product(category=category, company=self.company)

        with self.assertRaises(ValidationError):
            parent_category.company_id = self.company_2

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
