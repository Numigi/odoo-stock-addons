# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockVirtualAdjustment(models.Model):

    _name = "stock.virtual.adjustment"
    _description = "Virtual Inventory Adjustment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name desc"

    name = fields.Char(readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.user.company_id
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        readonly=True,
        required=True,
        copy=False,
    )

    location_id = fields.Many2one("stock.location", required=True)
    location_dest_id = fields.Many2one(
        "stock.location", required=True, string="Destination Location"
    )

    adjustment_date = fields.Datetime(required=True)
    reversal_date = fields.Datetime(required=True)

    note = fields.Char(copy=False)

    move_ids = fields.Many2many(
        "stock.move",
        "stock_virtual_adjustment_move_rel",
        "adjustment_id",
        "move_id",
        "Stock Moves",
        copy=False
    )

    line_ids = fields.One2many(
        "stock.virtual.adjustment.line",
        "adjustment_id",
    )

    @api.model
    def create(self, vals):
        adjustment = super().create(vals)
        adjustment._set_name_from_sequence()
        return adjustment

    @api.multi
    def copy(self, default=None):
        adjustment = super().copy()

        for line in self.line_ids:
            line.copy({"adjustment_id": adjustment.id})

        return adjustment

    def _set_name_from_sequence(self):
        self.name = (
            self.env["ir.sequence"]
            .with_context(force_company=self.company_id.id)
            .next_by_code("stock.virtual.adjustment")
        )

    def confirm(self):
        self._check_dates()

        for line in self.mapped("line_ids"):
            line._confirm()

        self.write({"state": "done"})

    def cancel(self):
        self._check_can_cancel()
        self.write({"state": "cancelled"})

    def set_to_draft(self):
        self._check_can_set_to_draft()
        self.write({"state": "draft"})

    def _check_dates(self):
        for adjustment in self:
            if adjustment.reversal_date >= datetime.now():
                raise ValidationError(
                    _(
                        "The adjustment {adjustment} could not be confirmed. "
                        "The reversal date ({date}) must be in the past."
                    ).format(
                        adjustment=adjustment.display_name,
                        date=adjustment.reversal_date,
                    )
                )

            if adjustment.reversal_date <= adjustment.adjustment_date:
                raise ValidationError(
                    _(
                        "The adjustment {adjustment} could not be confirmed. "
                        "The reversal date ({reversal_date}) must be after "
                        "the adjustment date ({adjustment_date})."
                    ).format(
                        adjustment=adjustment.display_name,
                        adjustment_date=adjustment.adjustment_date,
                        reversal_date=adjustment.reversal_date,
                    )
                )

    def _check_can_cancel(self):
        for adjustment in self:
            if adjustment.state == "done":
                raise ValidationError(
                    _(
                        "You can not cancel the adjustment {} "
                        "because it is already done."
                    ).format(adjustment.display_name)
                )

    def _check_can_set_to_draft(self):
        for adjustment in self:
            if adjustment.state == "done":
                raise ValidationError(
                    _(
                        "You can not set the adjustment {} to draft "
                        "because it is already done."
                    ).format(adjustment.display_name)
                )
