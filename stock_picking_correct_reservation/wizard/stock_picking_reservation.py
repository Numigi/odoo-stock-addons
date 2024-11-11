# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingReservation(models.TransientModel):
    _name = "stock.picking.reservation"
    _description = "Stock Picking Reservation"

    def action_correct_reservation(self):
        """"
        This function was inspired by the server action Correct inconsistencies for
        reservation
        """
        context = dict(self._context or {})
        pickings = context.get('active_ids', False)
        if not pickings:
            return {"type": "ir.actions.act_window_close"}
        picking_ids = self.env["stock.picking"].browse(pickings)
        move_line_ids = []
        move_line_to_recompute_ids = []
        logging = ''
        for picking in picking_ids:
            quants = self.env['stock.quant'].sudo().search(
                [('product_id', 'in', picking.move_line_ids.mapped('product_id.id'))]
            )
            for quant in quants:

                move_lines = self._get_matching_move_lines(quant)

                move_line_ids += move_lines.ids
                reserved_on_move_lines = sum(move_lines.mapped('product_qty'))
                move_line_str = ", ".join(map(str, move_lines.ids))

                if quant.location_id.should_bypass_reservation():
                    # If a quant is in a location that should bypass the reservation,
                    # its `reserved_quantity` field should be 0.
                    logging += self._handle_bypass_reservation(
                        quant, move_lines, reserved_on_move_lines, move_line_str
                    )
                else:
                    # If a quant is in a reservable location, its `reserved_quantity`
                    # should be exactly the sum of the `product_qty` of all the
                    # partially_available / assigned move lines with the same
                    # characteristics.
                    logging += self._handle_reservable_location(
                        quant, move_lines, reserved_on_move_lines,
                        move_line_str, move_line_to_recompute_ids
                    )

            move_lines_to_unreserve, unreserve_logging = self._find_unlinked_move_lines(
                move_line_ids
            )
            logging += unreserve_logging
            self._unreserve_move_lines(move_lines_to_unreserve)

            if logging:
                self._create_logging(logging)

            if move_line_to_recompute_ids:
                self.env['stock.move.line'].browse(
                    move_line_to_recompute_ids
                ).move_id._recompute_state()

        return {'type': 'ir.actions.act_window_close'}

    def _get_matching_move_lines(self, quant):
        return self.env["stock.move.line"].search(
            [
                ("product_id", "=", quant.product_id.id),
                ("location_id", "=", quant.location_id.id),
                ("lot_id", "=", quant.lot_id.id),
                ("package_id", "=", quant.package_id.id),
                ("owner_id", "=", quant.owner_id.id),
                ("product_qty", "!=", 0),
            ]
        )

    def _handle_bypass_reservation(self, quant, move_lines, reserved_on_move_lines,
                                   move_line_str):
        logging = ''
        if quant.reserved_quantity != 0:
            logging += (f"""Problematic quant found: {quant.id} (quantity: {quant.quantity},
                        reserved_quantity: {quant.reserved_quantity})\n"""
                        f"""its `reserved_quantity` field is not 0 while its location
                        should bypass the reservation\n""")
            if move_lines:
                logging += (
                    f"""These move lines are reserved on it:\n"""
                    f"""{move_line_str} (sum of the reservation:
                        {reserved_on_move_lines})\n"""
                    "******************\n"
                )
            else:
                logging += (
                    f"""no move lines are reserved on it, you can safely reset its
                    `reserved_quantity` to 0\n"""
                    f"""{move_line_str} (sum of the reservation:
                        {reserved_on_move_lines})\n"""
                    "******************\n"
                )
            quant.write({'reserved_quantity': 0})
        return logging

    def _handle_reservable_location(
        self,
        quant,
        move_lines,
        reserved_on_move_lines,
        move_line_str,
        move_line_to_recompute_ids,
    ):
        logging = ""
        if (
            quant.reserved_quantity in [0, -1]
            or quant.reserved_quantity != reserved_on_move_lines
        ):
            logging += (
                f"""Problematic quant found: {quant.id} (quantity: {quant.quantity},
                reserved_quantity: {quant.reserved_quantity})\n"""
                f"""{'its `reserved_quantity` field is 0' if
                     quant.reserved_quantity == 0 else
                     'its `reserved_quantity` field is negative' if
                     quant.reserved_quantity < 0 else
                     'its `reserved_quantity` does not reflect the move lines reservation'
                }\n"""
                f"""These move lines are reserved on it: {move_line_str}
                (sum of the reservation: {reserved_on_move_lines})\n"""
                "******************\n"
            )
            quant.write({"reserved_quantity": 0})
            move_lines.with_context(bypass_reservation_update=True).sudo().write(
                {"product_uom_qty": 0}
            )
            move_line_to_recompute_ids += move_lines.ids
        elif any(move_line.product_qty < 0 for move_line in move_lines):
            logging += (
                f"""Problematic quant found: {quant.id} (quantity: {quant.quantity},
                reserved_quantity: {quant.reserved_quantity})\n"""
                f"""its `reserved_quantity` correctly reflects the move lines
                reservation but some are negative\n"""
                f"""These move lines are reserved on it: {move_line_str}
                (sum of the reservation: {reserved_on_move_lines})\n"""
                "******************\n"
            )
            quant.write({"reserved_quantity": 0})
            move_lines.with_context(bypass_reservation_update=True).sudo().write(
                {"product_uom_qty": 0}
            )
            move_line_to_recompute_ids += move_lines.ids
        return logging

    def _find_unlinked_move_lines(self, move_line_ids):
        move_lines = self.env["stock.move.line"].search(
            [
                ("product_id.type", "=", "product"),
                ("product_qty", "!=", 0),
                ("id", "not in", move_line_ids),
            ]
        )
        move_lines_to_unreserve = []
        logging = ""
        for move_line in move_lines:
            if not move_line.location_id.should_bypass_reservation():
                logging += (
                    f"""Problematic move line found:
                    {move_line.id} (reserved_quantity:
                    {move_line.product_qty})\n"""
                    "There is no existing quant despite its `reserved_quantity`\n"
                    "******************\n"
                )
                move_lines_to_unreserve.append(move_line.id)
        return move_lines_to_unreserve, logging

    def _unreserve_move_lines(self, move_lines_to_unreserve):
        if move_lines_to_unreserve:
            query = """ UPDATE stock_move_line SET product_uom_qty = 0,
            product_qty = 0 WHERE id IN %s """
            self.env.cr.execute(query, (tuple(move_lines_to_unreserve),))

    def _create_logging(self, logging):
        self.env['ir.logging'].sudo().create({
            'name': 'Unreserve stock.quant and stock.move.line',
            'type': 'server',
            'level': 'DEBUG',
            'dbname': self.env.cr.dbname,
            'message': logging,
            'func': '_update_reserved_quantity',
            'path': 'addons/stock/models/stock_quant.py',
            'line': '0',
        })
