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
        "stock_dropshipping",  # Used for testing stock_warehouse_access
        # 'stock_immediate_transfer_disable',  # not ported to 12.0
        # 'stock_move_list_cost',  # not ported to 12.0
        # 'stock_move_origin_link',  # not ported to 12.0
        # 'stock_picking_show_address',  # not ported to 12.0
        "purchase_warehouse_access",
        "stock_component",
        "stock_component_account",
        "stock_inventory_accounting_date_editable",
        "stock_inventory_category_domain",
        "stock_inventory_internal_location",
        "stock_inventory_line_domain",
        "stock_inventory_line_domain_barcode",
        "stock_location_position_alphanum",
        "stock_picking_add_transit",
        "stock_picking_add_transit_rental",
        "stock_picking_change_destination",
        "stock_serial_single_quant",
        "stock_theorical_quantity_access",
        "stock_turnover_rate",
        "stock_turnover_rate_purchase",
        "stock_warehouse_access",
        "stock_warehouse_distance",
    ],
    "installable": True,
}
