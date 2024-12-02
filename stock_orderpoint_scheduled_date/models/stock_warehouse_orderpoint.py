# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class stockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    scheduled_date = fields.Date(
        "Scheduled Date", help="The date when this replenishment should be scheduled."
    )

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "scheduled_date",
    )
    def _compute_lead_days(self):
        for orderpoint in self:
            # Pass scheduled_date via context for lead time computation
            super(
                stockWarehouseOrderpoint,
                orderpoint.with_context(scheduled_date=orderpoint.scheduled_date),
            )._compute_lead_days()

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "scheduled_date",
    )
    def _compute_json_popover(self):
        for orderpoint in self:
            # Pass scheduled_date and delay description context
            super(
                stockWarehouseOrderpoint,
                orderpoint.with_context(
                    scheduled_date=orderpoint.scheduled_date,
                    bypass_delay_description=False,
                ),
            )._compute_json_popover()

    @api.model
    def action_open_set_schedule_date_wizard(self):
        """Open a wizard to set the scheduled date."""
        wizard = self.env["stock.warehouse.orderpoint.schedule.date"].create({})
        wizard.orderpoint_ids = self
        action = wizard.get_formview_action()
        action["target"] = "new"
        action["name"] = _("Set Schedule Date")
        return action

    @api.model
    def action_open_orderpoints(self):
        """Override to pass scheduled_date in the context."""
        return super(
            stockWarehouseOrderpoint,
            self.with_context(scheduled_date=self.scheduled_date),
        ).action_open_orderpoints()

    def _procure_orderpoint_confirm(
        self, use_new_cursor=False, company_id=None, raise_user_error=True
    ):
        """Ensure orderpoints with different scheduled dates aren't processed together."""
        scheduled_dates = set(self.mapped("scheduled_date"))
        if len(scheduled_dates) > 1:
            raise ValidationError(
                _("Please select lines with the same scheduled date.")
            )
        return super(
            stockWarehouseOrderpoint,
            self.with_context(scheduled_date=self[0].scheduled_date),
        )._procure_orderpoint_confirm(use_new_cursor, company_id, raise_user_error)

    def _prepare_procurement_values(self, date=False, group=False):
        """Prepare procurement values with consideration for the scheduled date."""
        values = super()._prepare_procurement_values(date=date, group=group)
        if self.scheduled_date:
            values["date_planned"] = self.scheduled_date
            values["date_deadline"] = self.scheduled_date
            # Reset scheduled_date after processing
            self.scheduled_date = False
        return values
