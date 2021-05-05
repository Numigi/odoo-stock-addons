# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockRentalConversionWizard(models.TransientModel):

    _inherit = "stock.rental.conversion.wizard"

    conversion_account_id = fields.Many2one(
        "account.account", "Expense Account", domain=[("deprecated", "=", False)]
    )

    def validate(self):
        if self.conversion_account_id:
            self = self.with_context(
                force_stock_input_output_account=self.conversion_account_id.id
            )

        return super(StockRentalConversionWizard, self).validate()

    @api.onchange("sales_product_id")
    def _onchange_sale_product_set_conversion_account(self):
        for wizard in self:
            wizard.conversion_account_id = (
                wizard.sales_product_id.rental_conversion_account_id
            )
