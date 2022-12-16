# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime, date, timedelta
from odoo import api, fields, models
from typing import Iterable, Optional
from .config import get_stock_turnover_days

_logger = logging.getLogger(__name__)

MAX_TURNOVER_RATE = 9999


def get_current_stock_quantity(product: 'Product') -> float:
    """Get the current quantity in stock of the given product.

    :param product: the product for which to sum quantities.
    """
    query = """
        SELECT sum(qt.quantity)
        FROM stock_quant qt
        JOIN stock_location loc ON qt.location_id = loc.id
        WHERE loc.usage = 'internal'
        AND qt.product_id = %s
    """
    product.env.cr.execute(query, (product.id, ))
    result = product.env.cr.fetchone()[0]
    return 0 if result is None else result


def get_moved_quantity(
    product: 'Product', date_from: date, date_to: date,
    origin_usages: Optional[Iterable[str]] = None,
    destination_usages: Optional[Iterable[str]] = None,
) -> float:
    """Get the stock move quantities for the given time range and locations.

    :param product: the product for which to sum quantities.
    :param date_from: the beginning of the time range
    :param date_to: the end of the time range
    :origin_usages: the origin types of origin locations to contrain
    :destination_usages: the origin types of destination locations to contrain
    """
    query = """
        SELECT sum(move.product_uom_qty)
        FROM stock_move move
        JOIN stock_location origin ON move.location_id = origin.id
        JOIN stock_location destination ON move.location_dest_id = destination.id
        WHERE move.product_id = %s
        AND move.date >= %s
        AND move.date < %s
        AND move.state = 'done'
    """
    date_from_str = fields.Date.to_string(date_from)
    date_to_str = fields.Date.to_string(date_to)
    query_params = [product.id, date_from_str, date_to_str]

    if origin_usages:
        query += "AND origin.usage in %s"
        query_params.append(tuple(origin_usages))

    if destination_usages:
        query += "AND destination.usage in %s"
        query_params.append(tuple(destination_usages))

    product.env.cr.execute(query, query_params)
    result = product.env.cr.fetchone()[0]
    return 0 if result is None else result


def get_delivered_quantity(
    product: 'Product', date_from: date, date_to: date
) -> float:
    """Get the current quantity in stock of the given product."""
    return get_moved_quantity(
        product, date_from, date_to,
        origin_usages=('internal', 'supplier'),
        destination_usages=('customer', ),
    )


def get_incomming_quantity(
    product: 'Product', date_from: date, date_to: date
) -> float:
    """Get the current quantity in stock of the given product."""
    return get_moved_quantity(
        product, date_from, date_to,
        destination_usages=('internal', ),
    )


def get_outgoing_quantity(
    product: 'Product', date_from: date, date_to: date
) -> float:
    """Get the current quantity in stock of the given product."""
    return get_moved_quantity(
        product, date_from, date_to,
        origin_usages=('internal', ),
    )


class Product(models.Model):

    _inherit = 'product.product'

    turnover_rate_active = fields.Boolean()
    turnover_rate = fields.Float(
        'Effective Turnover Rate',
        digits=(16, 2), readonly=True
    )
    target_turnover_rate = fields.Float(
        related='categ_id.target_turnover_rate',
        store=True,
        readonly=True,
    )

    def compute_turnover_rate(self):
        current_quantity = get_current_stock_quantity(self)
        interval_in_days = get_stock_turnover_days(self.env)
        date_from = datetime.now().date() - timedelta(interval_in_days + 1)
        date_to = datetime.now().date()
        incoming_quantity_cmp = self.with_context(from_date=date_from, to_date=date_to).incoming_qty
        incomming_quantity = get_incomming_quantity(self, date_from, date_to)
        outgoing_quantity = get_outgoing_quantity(self, date_from, date_to)
        delivered_quantity = get_delivered_quantity(self, date_from, date_to)
        start_quantity = current_quantity - outgoing_quantity + incomming_quantity
        average_quantity = (current_quantity + start_quantity) / 2
        if delivered_quantity == 0:

            turnover_rate = 0
        elif average_quantity == 0:
            turnover_rate = MAX_TURNOVER_RATE
        else:
            turnover_rate = delivered_quantity / average_quantity

        self.turnover_rate = turnover_rate

    @api.model
    def schedule_compute_turnover_rate(self):
        products = self.env['product.product'].search([
            ('type', '=', 'product'),
        ])
        _logger.info(
            "Scheduling the computation of turnover rates for {} products."
            .format(len(products))
        )

        for product in products:
            product.with_context(
                company_id=product.company_id.id).with_delay().compute_turnover_rate()
