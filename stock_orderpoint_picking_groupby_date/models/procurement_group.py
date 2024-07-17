from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    scheduled_date = fields.Date(
        string="Scheduled Date",
        default=fields.Datetime.now,
    )

    @api.model
    def _get_rule(self, product_id, location_id, values):
        rule = super()._get_rule(product_id, location_id, values)
        if rule and values.get("date_planned", False):
            values["group_id"] = rule._get_procurement_group(values.get("date_planned"))
        return rule
