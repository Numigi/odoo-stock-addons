# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models, fields, _


class StockZeroCostWizard(models.TransientModel):
    _name = 'stock.zero.cost.wizard'
    _description = 'Zero Cost Confirmation Wizard'

    # Link to the origin document (Only one will be filled)
    picking_id = fields.Many2one('stock.picking', string='Transfer')
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment')

    message = fields.Text(string="Warning", readonly=True)

    def action_confirm(self):
        """
        Triggered when the authorized user clicks 'Validate'.
        Passes the bypass flag and the approval note through the context.
        """
        self.ensure_one()

        # 1. Prepare the tracking note
        note = _("Action Forced: Zero cost valuation explicitly approved by %s on %s.") % (
            self.env.user.name, fields.Datetime.now()
        )

        # 2. Inject the bypass flag and the note into the execution context
        ctx = dict(self.env.context, skip_zero_cost_check=True, zero_cost_approval_note=note)

        # 3. Resume validation based on the source document
        if self.picking_id:
            self.picking_id.message_post(body=note)
            return self.picking_id.with_context(ctx).button_validate()

        elif self.production_id:
            self.production_id.message_post(body=note)
            return self.production_id.with_context(ctx).button_mark_done()

        elif self.inventory_id:
            self.inventory_id.message_post(body=note)
            return self.inventory_id.with_context(ctx).action_validate()
