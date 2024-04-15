# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class stockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    scheduled_date = fields.Date("Scheduled Date")

    @api.depends('rule_ids', 'product_id.seller_ids',
                 'product_id.seller_ids.delay', 'scheduled_date')
    def _compute_lead_days(self):
        for orderpoint in self.with_context(bypass_delay_description=True):
            if not orderpoint.scheduled_date:
                return super(stockWarehouseOrderpoint, orderpoint)._compute_lead_days()
            else:
                orderpoint.lead_days_date = orderpoint.scheduled_date

    def open_set_schedule_date_wizard(self):
        wizard = self.env['stock.warehouse.orderpoint.schedule.date'].create({})
        wizard.orderpoint_ids = self
        action = wizard.get_formview_action()
        action['target'] = 'new'
        action['name'] = _('Set Schedule Date')
        return action
