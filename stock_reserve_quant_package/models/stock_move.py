# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from collections import defaultdict
from odoo.tools.float_utils import float_compare, float_is_zero


class MyStockMove(models.Model):
    _inherit = "stock.move"

    def _check_move_map_quant_package(self, package, moves):
        """
        Check if the package can fully fulfill the products in the given moves.
        The package will only be considered if:
        1. It contains all the required products with exact or higher quantities.
        2. All products in the package have corresponding moves.
        3. The moves must fulfill the **entire** quantity in the package
        for every product.
        """
        # Group quants by product and sum their quantities in the package
        grouped_quants = defaultdict(float)
        for quant in package.quant_ids:
            grouped_quants[quant.product_id] += quant.quantity

        # Group moves by product and sum their required quantities
        grouped_ops = defaultdict(float)
        for move in moves:
            grouped_ops[move.product_id] += move.product_uom_qty

        # Ensure that all products in the package have moves and
        # their quantities exactly match
        all_fulfilled = all(
            grouped_ops.get(product, 0) == grouped_quants.get(product, 0)
            for product in grouped_quants
        )

        # Return the matching moves for the package only if
        # all quantities are fully fulfilled
        package_moves = self.env['stock.move']
        if all_fulfilled:
            package_moves = moves.filtered(lambda m: m.product_id in grouped_quants)

        return package_moves

    def _get_quant_package_to_reserve(self, moves):
        """
        Find the packages that can fully fulfill the moves. 
        If no package can fulfill the moves, it returns un-packaged products.
        """
        # Search for quants that are not reserved and
        # match the products and locations in the moves
        quants = self.env['stock.quant'].search(
            [('product_id', 'in', moves.mapped('product_id').ids),
             ('location_id', 'in', moves.mapped('location_id').ids),
             ('reserved_quantity', '=', 0),
             ('quantity', '>', 0),
             ('package_id', '!=', False)],
            order="package_id desc"
        )

        # Prefetch necessary fields to improve performance
        packages = quants.mapped('package_id').with_context(prefetch_fields=False)

        # Sort packages by the number of quants they contain,
        # prioritizing larger packages
        packages = sorted(packages, key=lambda p: len(p.quant_ids), reverse=True)

        next_moves = moves
        package_moves_map = defaultdict(list)
        if not packages:
            return package_moves_map

        # Try to find packages that can fully cover the moves
        for package in packages:
            # If package has reserved Quants pass to next package
            if package.quant_ids.filtered(lambda q: q.reserved_quantity):
                continue
            if next_moves:
                # Check if the package can completely fulfill some moves
                package_moves = self._check_move_map_quant_package(
                    package, next_moves
                )
                if package_moves:
                    package_moves_map[package] = package_moves
                    # Subtract the moves covered by the package from
                    # the remaining moves
                    next_moves = next_moves - package_moves_map[package]
        # If there are still unfulfilled moves, or no package was found,
        # assign the un-packaged moves
        if next_moves or not package_moves_map:
            package_moves_map[None] = next_moves
        return package_moves_map

    def _action_assign(self):
        moves = self.filtered(
            lambda m: m.state in ['confirmed', 'waiting', 'partially_available']
        )
        moves_by_package = self._get_quant_package_to_reserve(moves)
        if not moves_by_package:
            return super(MyStockMove, self)._action_assign()
        package_list = list(moves_by_package.keys())
        for package in package_list:
            for move in moves_by_package[package]:
                if move.location_id.should_bypass_reservation()\
                        or move.product_id.type == 'consu':
                    continue
                else:
                    if not move.move_orig_ids:
                        if move.procure_method == 'make_to_order':
                            continue
                        assigned_moves = self.env['stock.move']
                        rounding = move.product_id.uom_id.rounding
                        missing_reserved_uom_quantity = (
                            move.product_uom_qty - move.reserved_availability
                        )
                        missing_reserved_quantity = move.product_uom._compute_quantity(
                            missing_reserved_uom_quantity,
                            move.product_id.uom_id,
                            rounding_method='HALF-UP'
                        )
                        # If we don't need any quantity, consider the move assigned.
                        need = missing_reserved_quantity
                        if float_is_zero(need, precision_rounding=rounding):
                            assigned_moves |= move
                            continue
                        forced_package_id = (move.package_level_id.package_id
                                             or package or None)
                        available_quantity = \
                            self.env['stock.quant'].with_context(
                                reserve_full_package=True
                                )._get_available_quantity(
                                move.product_id, move.location_id,
                                package_id=forced_package_id
                            )
                        if available_quantity <= 0:
                            self = self - move
                            continue
                        taken_quantity = \
                            move.with_context(
                                reserve_full_package=True
                                )._update_reserved_quantity(
                                need, available_quantity,
                                move.location_id, package_id=forced_package_id,
                                strict=False
                            )
                        if float_is_zero(taken_quantity,
                                         precision_rounding=rounding):
                            self = self - move
                            continue
                        if float_compare(need, taken_quantity,
                                         precision_rounding=rounding) == 0:
                            assigned_moves |= move
                        else:
                            self = self - move
                    else:
                        continue
        return super(MyStockMove, self)._action_assign()
