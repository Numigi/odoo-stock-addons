# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _account_entry_move(self):
        res = super()._account_entry_move()
        self._generate_parent_missing_interim_entries()
        return res

    def _generate_parent_missing_interim_entries(self):
        for parent_move in self.mapped("parent_id"):
            parent_move._generate_missing_interim_entries()
            parent_move._generate_parent_missing_interim_entries()

    def _generate_missing_interim_entries(self):
        items_to_reconcile = self._find_component_items_to_reconcile()

        for item in items_to_reconcile:
            self._generate_component_interim_entry(item)

    def _find_component_items_to_reconcile(self):
        product_interim_account = self._get_product_output_account()
        journal_items = self.mapped("child_ids.account_move_ids.line_ids")
        return journal_items.filtered(
            lambda i: i.account_id.reconcile
            and i.account_id == product_interim_account
            and not i.reconciled
        )

    def _generate_component_interim_entry(self, journal_item):
        move_vals = self._get_component_interim_move_vals(journal_item)

        component_vals = self._get_component_interim_move_line_vals(journal_item)
        equipment_vals = self._get_equipment_interim_move_line_vals(journal_item)

        move_vals["line_ids"] = [(0, 0, component_vals), (0, 0, equipment_vals)]
        move = self.env["account.move"].sudo().create(move_vals)
        move.post()

        new_component_item = move.line_ids.sorted("id")[0]
        (new_component_item | journal_item).reconcile()

    def _get_component_interim_move_vals(self, journal_item):
        date = self._context.get("force_period_date", fields.Date.context_today(self))
        return {
            "ref": self.picking_id.name,
            "date": date,
            "journal_id": journal_item.move_id.journal_id.id,
            "company_id": journal_item.company_id.id,
            "stock_move_id": self.id,
        }

    def _get_component_common_move_line_vals(self, journal_item):
        return {
            "name": "{}: {}".format(self.name, journal_item.name),
            "quantity": 1,
            "uom_id": self.env.ref("uom.product_uom_unit").id,
            "partner_id": self._get_partner_id_for_valuation_lines(),
            "ref": self.picking_id.name,
        }

    def _get_component_interim_move_line_vals(self, journal_item):
        vals = self._get_component_common_move_line_vals(journal_item)
        vals.update(
            {
                "product_id": journal_item.product_id.id,
                "account_id": journal_item.account_id.id,
                "debit": journal_item.credit,
                "credit": journal_item.debit,
            }
        )
        return vals

    def _get_equipment_interim_move_line_vals(self, journal_item):
        vals = self._get_component_common_move_line_vals(journal_item)
        vals.update(
            {
                "product_id": self.product_id.id,
                "account_id": self._get_product_output_account().id,
                "debit": journal_item.debit,
                "credit": journal_item.credit,
            }
        )
        return vals

    def _get_product_output_account(self):
        product_accounts = self.product_id.product_tmpl_id._get_product_accounts()
        return product_accounts["stock_output"]
