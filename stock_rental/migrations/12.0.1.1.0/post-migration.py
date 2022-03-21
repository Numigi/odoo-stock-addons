import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    warehouses = env["stock.warehouse"].search([])
    locations = warehouses.mapped("rental_location_id")

    for location in _iter_children_locations(locations):
        _logger.info(
            "Setting stock location {} as stock rental".format(location.id)
        )
        location.is_rental_stock_location = True


def _iter_children_locations(locations):
    for location in locations:
        yield location

    children = locations.mapped("child_ids")
    if children:
        yield from _iter_children_locations(children)
