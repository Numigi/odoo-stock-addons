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
        "res.company",
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
        states={"draft": [("readonly", False)]},
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
        track_visibility="onchange",
    )

    location_id = fields.Many2one(
        "stock.location",
        required=True,
        track_visibility="onchange",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        required=True,
        readonly=True,
        string="Destination Location",
        track_visibility="onchange",
        states={"draft": [("readonly", False)]},
    )

    adjustment_date = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility="onchange",
        states={"draft": [("readonly", False)]},
    )
    reversal_date = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility="onchange",
        states={"draft": [("readonly", False)]},
    )

    notes = fields.Char(copy=False)

    move_ids = fields.Many2many(
        "stock.move",
        "stock_virtual_adjustment_move_rel",
        "adjustment_id",
        "move_id",
        "Stock Moves",
        copy=False,
        readonly=True,
    )
    stock_move_count = fields.Integer(compute="_compute_stock_move_count")

    line_ids = fields.One2many(
        "stock.virtual.adjustment.line",
        "adjustment_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _compute_stock_move_count(self):
        for adjustment in self:
            adjustment.stock_move_count = len(adjustment.move_ids)

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

    def view_stock_moves(self):
        action = self.env.ref(
            "stock_virtual_adjustment.action_view_stock_moves"
        ).read()[0]
        action["domain"] = [("id", "in", self.move_ids.ids)]
        return action

    def _check_dates(self):
        for adjustment in self:
            if adjustment.reversal_date >= datetime.now():
                raise ValidationError(
                    _(
                        "The adjustment {adjustment} could not be confirmed. "
                        "The reversal date ({reversal_date}) must be in the past."
                    ).format(
                        adjustment=adjustment.display_name,
                        reversal_date=adjustment._get_context_reversal_date(),
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
                        adjustment_date=adjustment._get_context_adjustment_date(),
                        reversal_date=adjustment._get_context_reversal_date(),
                    )
                )

    def _get_context_adjustment_date(self):
        return fields.Datetime.context_timestamp(self, self.adjustment_date)

    def _get_context_reversal_date(self):
        return fields.Datetime.context_timestamp(self, self.reversal_date)

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
