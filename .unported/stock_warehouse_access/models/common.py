# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND


def check_records_location_id_access(records: models.Model, error_message: str, context: dict):
    """Check the access to the location related to the given records.

    This function can be used to check access for models that have a location_id
    field.

    It raises AccessError if one record can not be accessed.

    :param records: the records to check.
    :param error_message: the message to display in case of access error.
        It must contain 2 fields `{record}` and `{location}`.
    :param context: the odoo context for translations
    """
    user = records.env.user
    for record in records:
        location = record.location_id
        warehouse = location.get_warehouse()
        if warehouse and not user.has_warehouse_access(warehouse):
            raise AccessError(_(error_message).format(
                record=record.display_name, location=location.display_name))


def get_domain_with_location_id_filter(env: api.Environment, initial_domain: list) -> list:
    """Extend the given domain with location_id access filter.

    This function can be used to check access for models that have a location_id
    field.

    :param env: the odoo environment
    :param initial_domain: the search domain to extend
    :return: the domain with security filters
    """
    if not env.user.all_warehouses:
        unauthorized_location_ids = env.user.get_unauthorized_location_ids()
        return AND((initial_domain, [('location_id', 'not in', unauthorized_location_ids)]))
    return initial_domain


def _move_has_location_access(move: models.Model, location) -> bool:
    """Evaluate whether the user has access to the given location of the stock-move like record.

    :param move: the stock-move-like record to evaluate.
    :param location: the location to evaluate.
    """
    warehouse = location.get_warehouse()
    user = move.env.user
    warehouse_unauthorized = (warehouse and not user.has_warehouse_access(warehouse))
    return not warehouse_unauthorized


def check_stock_move_access(records: models.Model, error_message: str, context: dict):
    """Check the access to the location related to the given move-like records.

    This function can be used to check access for models that have location_id
    and location_dest_id fields.

    It raises AccessError if one record can not be accessed.

    :param records: the records to check.
    :param error_message: the message to display in case of access error.
        It must contain 2 fields `{record}` and `{location}`.
    :param context: the odoo context for translations
    """
    for record in records:
        for location in (record.location_id | record.location_dest_id):
            if not _move_has_location_access(record, location):
                raise AccessError(_(error_message).format(
                    record=record.display_name, location=location.display_name))


def get_domain_with_stock_move_filter(env: api.Environment, initial_domain) -> list:
    """Get the security domain to filter stock-move-like records per warehouse.

    This method works for models with location_id and location_dest_id fields.

    :param env: the odoo environment
    :return: the search domain
    """
    if not env.user.all_warehouses:
        unauthorized_location_ids = env.user.get_unauthorized_location_ids()
        return AND((initial_domain, [
            '&',
            ('location_id', 'not in', unauthorized_location_ids),
            ('location_dest_id', 'not in', unauthorized_location_ids),
        ]))
    return initial_domain
