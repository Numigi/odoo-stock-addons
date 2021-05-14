# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, modules, tools


class StockRule(models.Model):

    _inherit = "stock.rule"

    special_route_id = fields.Many2one(
        "stock.location.route",
        ondelete="restrict",
    )

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        modules.registry.Registry(self.env.cr.dbname).clear_caches()
        return res

    def write(self, vals):
        super().write(vals)
        modules.registry.Registry(self.env.cr.dbname).clear_caches()
        return True

    def unlink(self):
        super().unlink()
        modules.registry.Registry(self.env.cr.dbname).clear_caches()
        return True

    @tools.ormcache()
    def _get_procurement_rules_data(self):
        rules = self.sudo().search(
            [("action", "!=", "push")], order="route_sequence, sequence"
        )
        return [r._get_data_dict() for r in rules]

    def _get_data_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id.id,
            "warehouse_id": self.warehouse_id.id,
            "location_id": self.location_id.id,
            "route_id": self.route_id.id,
        }
