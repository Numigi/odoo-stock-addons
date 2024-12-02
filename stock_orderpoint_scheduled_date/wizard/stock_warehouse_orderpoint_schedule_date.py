# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class OrderpointScheduleDate(models.TransientModel):
    _name = 'stock.warehouse.orderpoint.schedule.date'
    _description = "Replanishment Schedule Date wizard"

    orderpoint_ids = fields.Many2many(
        'stock.warehouse.orderpoint',
        'stock_warehouse_orderpoint_schedule_date_rel',
        'wizard_id',
        'orderpoint_id',
        string='Order Points',
    )
    scheduled_date = fields.Date("Scheduled Date")

    def validate(self):
        self.ensure_one()
        self.orderpoint_ids.write({
            'scheduled_date': self.scheduled_date
        })
        return True
