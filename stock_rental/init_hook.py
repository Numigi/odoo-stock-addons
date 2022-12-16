# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _setup_warehouses_rental_routes(env)


def _setup_warehouses_rental_routes(env):
    main_company = env.ref("base.main_company")
    warehouses = env["stock.warehouse"].search([('company_id', '=', main_company.id)])
    for warehouse in warehouses:
        warehouse.setup_rental_route()
