# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = (
            super()._get_accounting_data_for_valuation()
        )

        forced_account_id = self._context.get("force_stock_input_output_account")
        if forced_account_id:
            acc_src = forced_account_id
            acc_dest = forced_account_id

        return journal_id, acc_src, acc_dest, acc_valuation
