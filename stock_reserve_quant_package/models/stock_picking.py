# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _check_entire_pack(self):
        """ This function check if entire packs are moved in the picking"""
        for picking in self:
            origin_packages = picking.move_line_ids.mapped("package_id")
            for pack in origin_packages:
                if picking._check_move_lines_map_quant_package(pack):
                    package_level_ids = picking.package_level_ids.filtered(
                        lambda pl: pl.package_id == pack)
                    move_lines_to_pack = \
                        picking.move_line_ids.filtered(
                            lambda ml: ml.package_id == pack and not
                            ml.result_package_id)
                    if not package_level_ids:
                        self.env['stock.package_level'].create({
                            'picking_id': picking.id,
                            'package_id': pack.id,
                            'location_id': pack.location_id.id,
                            'location_dest_id':
                                self._get_entire_pack_location_dest(
                                    move_lines_to_pack) or
                                picking.location_dest_id.id,
                            'move_line_ids': [(6, 0, move_lines_to_pack.ids)]
                        })
                        move_lines_to_pack.write({
                            'result_package_id': pack.id,
                        })
                    else:
                        move_lines_in_package_level = \
                            move_lines_to_pack.filtered(
                                lambda ml: ml.move_id.package_level_id)
                        move_lines_without_package_level = \
                            move_lines_to_pack - move_lines_in_package_level
                        for ml in move_lines_in_package_level:
                            ml.write({
                                'result_package_id': pack.id,
                                'package_level_id':
                                    ml.move_id.package_level_id.id,
                            })
                        move_lines_without_package_level.write({
                            'result_package_id': pack.id,
                            'package_level_id': package_level_ids[0].id,
                        })
                        for pl in package_level_ids:
                            pl.location_dest_id = \
                                self._get_entire_pack_location_dest(
                                    pl.move_line_ids) or \
                                picking.location_dest_id.id
                else:
                    picking.do_unreserve()
