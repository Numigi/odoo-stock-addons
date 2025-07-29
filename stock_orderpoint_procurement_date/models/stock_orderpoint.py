# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_date_per_tz(self, date):
        """Return the right date per company tz"""
        return (
            timezone(self.company_id.partner_id.tz or "UTC")
            .localize(datetime.combine(date, time(12)))
            .astimezone(UTC)
            .replace(tzinfo=None)
        )

    def _prepare_procurement_values(self, date=False, group=False):
        values = super()._prepare_procurement_values(date=date, group=group)
        date_planned = self._get_date_per_tz(values["date_planned"])
        date = self._get_date_per_tz(date)
        values["date_planned"] = date_planned
        values["date_deadline"] = date or False
        return values
