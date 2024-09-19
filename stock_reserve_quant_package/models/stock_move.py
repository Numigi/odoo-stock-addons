# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from itertools import groupby
from operator import itemgetter

from odoo import models
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.addons.stock.models.stock_move import StockMove


class MyStockMove(models.Model):
    _inherit = "stock.move"

    def _check_move_map_quant_package(self, moves, package):
        """ This method checks that all product of the package (quant) are well
         present in the moves of the picking. """
        all_in = True
        precision_digits = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        grouped_quants = {}
        for k, g in groupby(
                sorted(package.quant_ids, key=lambda q: q.product_id),
                key=lambda q: q.product_id):
            grouped_quants[k] = \
                sum(self.env['stock.quant'].browse(
                    list(g)[0].id).mapped('quantity'))

        grouped_ops = {}
        for k, g in groupby(
                sorted(moves, key=lambda m: m.product_id),
                key=lambda m: m.product_id):
            grouped_ops[k] = \
                sum(self.env['stock.move'].browse(
                    list(g)[0].id).mapped('product_uom_qty'))
        if any(not float_is_zero(
                grouped_quants.get(key, 0) - grouped_ops.get(key, 0),
                precision_digits=precision_digits) for key in grouped_quants):
            all_in = False
        return all_in

    def _get_quant_package_to_reserve(self, quant_package, move, moves):
        """ This method verify if all moves products exist in quants without
        package or if they belong to the same quant package.
        Then return the common package if exist"""
        packages = self.env['stock.quant'].search(
            [('product_id', '=', move.product_id.id),
             ('location_id', '=', move.location_id.id),
             ('reserved_quantity', '=', 0),
             ], order="package_id desc").mapped('package_id')
        if packages:
            # checks that all product of the package (quant)
            # are well present in the moves of the picking
            for package in packages:
                all_in = \
                    self._check_move_map_quant_package(
                        moves, package)
                if all_in:
                    quant_package = package
                    break
        return quant_package

    def _action_assign(self):
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        moves = self.filtered(
            lambda m: m.state in ['confirmed', 'waiting', 'partially_available']
        )
        for move in moves:
            quant_package = self.env['stock.quant.package']
            rounding = roundings[move]
            missing_reserved_uom_quantity = (
                move.product_uom_qty - reserved_availability[move]
            )
            missing_reserved_quantity = move.product_uom._compute_quantity(
                missing_reserved_uom_quantity,
                move.product_id.uom_id,
                rounding_method='HALF-UP'
            )
            if move.location_id.should_bypass_reservation()\
                    or move.product_id.type == 'consu':
                return super()._action_assign()
            else:
                if not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves |= move
                        continue
                    # check if we can reserve the whole package
                    quant_package = \
                        self._get_quant_package_to_reserve(
                            quant_package, move, moves)
                    if quant_package:
                        forced_package_id = \
                            move.package_level_id.package_id or \
                            quant_package or None
                    else:
                        forced_package_id = \
                            move.package_level_id.package_id or None
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    available_quantity = \
                        self.env['stock.quant']._get_available_quantity(
                            move.product_id, move.location_id,
                            package_id=forced_package_id
                        )
                    if available_quantity <= 0:
                        continue
                    taken_quantity = \
                        move._update_reserved_quantity(
                            need, available_quantity,
                            move.location_id, package_id=forced_package_id,
                            strict=False
                        )
                    if float_is_zero(taken_quantity,
                                     precision_rounding=rounding):
                        continue
                    if float_compare(need, taken_quantity,
                                     precision_rounding=rounding) == 0:
                        assigned_moves |= move
                    else:
                        partially_available_moves |= move
                else:
                    return super()._action_assign()
        return super()._action_assign()
