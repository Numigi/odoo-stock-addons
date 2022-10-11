# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _gather(self, product_id, location_id, lot_id=None, package_id=None,
                owner_id=None, strict=False):
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(
            removal_strategy)
        domain = [
            ('product_id', '=', product_id.id),
            ('package_id', '=', package_id and package_id.id or False)
        ]
        if not strict:
            if lot_id:
                domain = expression.AND(
                    [['|', ('lot_id', '=', lot_id.id), ('lot_id', '=', False)],
                     domain])
            if owner_id:
                domain = expression.AND(
                    [[('owner_id', '=', owner_id.id)], domain])
            domain = expression.AND(
                [[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([['|', ('lot_id', '=', lot_id.id),
                                      ('lot_id', '=', False)] if lot_id else [
                ('lot_id', '=', False)], domain])
            domain = expression.AND(
                [[('owner_id', '=', owner_id and owner_id.id or False)],
                 domain])
            domain = expression.AND(
                [[('location_id', '=', location_id.id)], domain])

        # Copy code of _search for special NULLS FIRST/LAST order
        self.sudo(self._uid).check_access_rights('read')
        query = self._where_calc(domain)
        self._apply_ir_rules(query, 'read')
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or ''
        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + " ORDER BY " + removal_strategy_order
        self._cr.execute(query_str, where_clause_params)
        res = self._cr.fetchall()
        # No uniquify list necessary as auto_join is not applied anyways...
        quants = self.browse([x[0] for x in res])
        quants = quants.sorted(lambda q: not q.lot_id)
        return quants
