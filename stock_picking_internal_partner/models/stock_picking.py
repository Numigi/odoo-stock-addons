# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        picking_type_id = self.env["stock.picking.type"].browse(
            vals.get('picking_type_id'))
        if picking_type_id.code == 'internal' and \
                picking_type_id.warehouse_as_partner:
            vals['partner_id'] = self._get_partner_address(vals).id
        return super(StockPicking, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            if vals.get('picking_type_id'):
                picking_type_id = self.env["stock.picking.type"].browse(
                    vals.get('picking_type_id'))
                if picking_type_id.code == 'internal' and \
                        picking_type_id.warehouse_as_partner:
                    vals['partner_id'] = record._get_partner_address(vals).id
        return super(StockPicking, self).write(vals)

    def _get_partner_address(self, vals):
        location_dest_id = vals.get('location_dest_id') or \
                          self.location_dest_id.id
        warehouse = self.env["stock.location"].browse(
            location_dest_id).get_warehouse()
        if not warehouse:
            company_id = vals.get('company_id') or self.company_id.id
            warehouse = self.env["stock.warehouse"].search([
                ('company_id', '=', company_id)
            ], limit=1)
        return warehouse.partner_id
