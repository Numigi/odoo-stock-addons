# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Main Module",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Install all addons required for testing.",
    "depends": [
        "onchange_helper",  # Used for testing stock_rental_conversion
        "stock_dropshipping",  # Used for testing stock_warehouse_access
        "purchase_warehouse_access",
        "stock_auto_assign_disabled",
        "stock_auto_assign_disabled_jit",
        "stock_component",
        "stock_component_account",
        "stock_immediate_transfer_disable",
        "stock_inventory_accounting_date_editable",
        "stock_inventory_category_domain",
        "stock_inventory_internal_location",
        "stock_inventory_line_domain",
        "stock_inventory_line_domain_barcode",
        "stock_location_position_alphanum",
        "stock_move_list_cost",
        "stock_move_location_domain_improved",
        "stock_move_origin_link",
        "stock_picking_add_transit",
        "stock_picking_add_transit_rental",
        "stock_picking_change_destination",
        "stock_picking_digitized_signature",
        "stock_picking_search_by_serial",
        "stock_picking_show_address",
        "stock_previous_step_return",
        "stock_product_location_info",
        "stock_rental",
        "stock_rental_conversion",
        "stock_rental_conversion_account",
        "stock_rental_conversion_asset",
        "stock_route_optimized",
        "stock_serial_asset",
        "stock_serial_no_simple_form",
        "stock_serial_single_quant",
        "stock_special_route",
        "stock_theorical_quantity_access",
        "stock_turnover_rate",
        "stock_turnover_rate_purchase",
        "stock_warehouse_access",
        "stock_warehouse_distance",
    ],
    "installable": True,
}
