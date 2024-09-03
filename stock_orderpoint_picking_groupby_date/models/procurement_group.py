from odoo import api, fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    scheduled_date = fields.Date(
        string="Scheduled Date",
        default=fields.Datetime.now,
    )
    from_orderpoint = fields.Boolean(string="From Replenishment")

    @api.model
    def _get_rule(self, product_id, location_id, values):
        rule = super()._get_rule(product_id, location_id, values)
        route_ids = values.get("route_ids", False)
        orderpoint_id = values.get("orderpoint_id", False)
        date_planned = values.get("date_planned", False)
        if rule and orderpoint_id and route_ids and date_planned:
            values["group_id"] = rule._get_procurement_group(
                date_planned, orderpoint_id
            )
        return super()._get_rule(product_id, location_id, values)
