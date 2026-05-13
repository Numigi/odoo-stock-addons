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
