FROM quay.io/numigi/odoo-public:12.latest
MAINTAINER numigi <contact@numigi.com>

USER root

ARG GIT_TOKEN

COPY .docker_files/test-requirements.txt ./test-requirements.txt
RUN pip3 install -r ./test-requirements.txt && rm ./test-requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY product_category_safe_change /mnt/extra-addons/product_category_safe_change
COPY purchase_warehouse_access /mnt/extra-addons/purchase_warehouse_access
COPY stock_adjustment_lines_display /mnt/extra-addons/stock_adjustment_lines_display
COPY stock_auto_assign_disabled /mnt/extra-addons/stock_auto_assign_disabled
COPY stock_auto_assign_disabled_jit /mnt/extra-addons/stock_auto_assign_disabled_jit
COPY stock_client_order_ref /mnt/extra-addons/stock_client_order_ref
COPY stock_component /mnt/extra-addons/stock_component
COPY stock_component_account /mnt/extra-addons/stock_component_account
COPY stock_extra_views /mnt/extra-addons/stock_extra_views
COPY stock_immediate_transfer_disable /mnt/extra-addons/stock_immediate_transfer_disable
COPY stock_inventory_accounting_date_editable /mnt/extra-addons/stock_inventory_accounting_date_editable
COPY stock_inventory_category_domain /mnt/extra-addons/stock_inventory_category_domain
COPY stock_inventory_internal_location /mnt/extra-addons/stock_inventory_internal_location
COPY stock_inventory_line_domain /mnt/extra-addons/stock_inventory_line_domain
COPY stock_inventory_line_domain_barcode /mnt/extra-addons/stock_inventory_line_domain_barcode
COPY stock_location_position_alphanum /mnt/extra-addons/stock_location_position_alphanum
COPY stock_move_list_cost /mnt/extra-addons/stock_move_list_cost
COPY stock_move_list_location /mnt/extra-addons/stock_move_list_location
COPY stock_move_location_domain_improved /mnt/extra-addons/stock_move_location_domain_improved
COPY stock_move_origin_link /mnt/extra-addons/stock_move_origin_link
COPY stock_move_valuation_adjustment /mnt/extra-addons/stock_move_valuation_adjustment
COPY stock_picking_add_transit /mnt/extra-addons/stock_picking_add_transit
COPY stock_picking_add_transit_rental /mnt/extra-addons/stock_picking_add_transit_rental
COPY stock_picking_change_destination /mnt/extra-addons/stock_picking_change_destination
COPY stock_picking_digitized_signature /mnt/extra-addons/stock_picking_digitized_signature
COPY stock_picking_internal_partner /mnt/extra-addons/stock_picking_internal_partner
COPY stock_picking_search_by_serial /mnt/extra-addons/stock_picking_search_by_serial
COPY stock_picking_show_address /mnt/extra-addons/stock_picking_show_address
COPY stock_picking_show_sale_order /mnt/extra-addons/stock_picking_show_sale_order
COPY stock_picking_tracking_reference /mnt/extra-addons/stock_picking_tracking_reference
COPY stock_previous_step_return /mnt/extra-addons/stock_previous_step_return
COPY stock_product_location_info /mnt/extra-addons/stock_product_location_info
COPY stock_quant_package_image /mnt/extra-addons//stock_quant_package_image
COPY stock_rental /mnt/extra-addons/stock_rental
COPY stock_rental_conversion /mnt/extra-addons/stock_rental_conversion
COPY stock_rental_conversion_account /mnt/extra-addons/stock_rental_conversion_account
COPY stock_rental_conversion_asset /mnt/extra-addons/stock_rental_conversion_asset
COPY stock_reserve_quant_package /mnt/extra-addons/stock_reserve_quant_package
COPY stock_route_optimized /mnt/extra-addons/stock_route_optimized
COPY stock_routes_product_multico /mnt/extra-addons/stock_routes_product_multico
COPY stock_same_location_disable_reservation /mnt/extra-addons/stock_same_location_disable_reservation
COPY stock_scheduler_include_rfq /mnt/extra-addons/stock_scheduler_include_rfq
COPY stock_serial_asset /mnt/extra-addons/stock_serial_asset
COPY stock_serial_no_simple_form /mnt/extra-addons/stock_serial_no_simple_form
COPY stock_serial_single_quant /mnt/extra-addons/stock_serial_single_quant
COPY stock_special_route /mnt/extra-addons/stock_special_route
COPY stock_theorical_quantity_access /mnt/extra-addons/stock_theorical_quantity_access
COPY stock_turnover_rate /mnt/extra-addons/stock_turnover_rate
COPY stock_turnover_rate_purchase /mnt/extra-addons/stock_turnover_rate_purchase
COPY stock_virtual_adjustment /mnt/extra-addons/stock_virtual_adjustment
COPY stock_warehouse_access /mnt/extra-addons/stock_warehouse_access
COPY stock_warehouse_distance /mnt/extra-addons/stock_warehouse_distance

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
