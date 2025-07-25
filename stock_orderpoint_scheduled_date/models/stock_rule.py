# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_lead_days(self, product):
        """Add the delay from the manually entered scheduled date in the replenishment
        order to the cumulative delay and cumulative description.
        """
        delay, delay_description = super()._get_lead_days(product)
        scheduled_date = self.env.context.get("scheduled_date")
        bypass_delay_description = self.env.context.get(
            "bypass_delay_description", False
        )
        if scheduled_date:
            # Convert the scheduled date from string to UTC datetime
            manual_delay = (scheduled_date - fields.Date.today()).days
            delay += manual_delay
            if not bypass_delay_description:
                delay_description += (
                    "<tr><td>%s</td><td class='text-right'>+ %d %s</td></tr>"
                    % (_("Manual Lead Time"), manual_delay, _("day(s)"))
                )
        return delay, delay_description
