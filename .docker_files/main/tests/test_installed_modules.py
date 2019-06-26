
from odoo.tests import TransactionCase


class TestModules(TransactionCase):
    """Test that Odoo modules are installed.

    Because some web modules have no python tests,
    we test that these modules are installed.
    """

    def setUp(self):
        super(TestModules, self).setUp()
        self.modules = self.env['ir.module.module']

    def test_module_installed(self):
        """Project Stage No Quick Create is installed."""
        self.assertTrue(self.modules.search([('name', '=', 'stock_move_origin_link')]))
