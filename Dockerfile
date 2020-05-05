FROM quay.io/numigi/odoo-public:12.0
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

COPY purchase_warehouse_access /mnt/extra-addons/purchase_warehouse_access
COPY stock_component /mnt/extra-addons/stock_component
COPY stock_component_account /mnt/extra-addons/stock_component_account
COPY stock_inventory_accounting_date_editable /mnt/extra-addons/stock_inventory_accounting_date_editable
COPY stock_inventory_category_domain /mnt/extra-addons/stock_inventory_category_domain
COPY stock_inventory_internal_location /mnt/extra-addons/stock_inventory_internal_location
COPY stock_inventory_line_domain /mnt/extra-addons/stock_inventory_line_domain
COPY stock_inventory_line_domain_barcode /mnt/extra-addons/stock_inventory_line_domain_barcode
COPY stock_location_position_alphanum /mnt/extra-addons/stock_location_position_alphanum
COPY stock_picking_add_transit /mnt/extra-addons/stock_picking_add_transit
COPY stock_picking_change_destination /mnt/extra-addons/stock_picking_change_destination
COPY stock_rental /mnt/extra-addons/stock_rental
COPY stock_rental_conversion /mnt/extra-addons/stock_rental_conversion
COPY stock_rental_conversion_asset /mnt/extra-addons/stock_rental_conversion_asset
COPY stock_serial_asset /mnt/extra-addons/stock_serial_asset
COPY stock_serial_no_simple_form /mnt/extra-addons/stock_serial_no_simple_form
COPY stock_serial_single_quant /mnt/extra-addons/stock_serial_single_quant
COPY stock_theorical_quantity_access /mnt/extra-addons/stock_theorical_quantity_access
COPY stock_turnover_rate /mnt/extra-addons/stock_turnover_rate
COPY stock_turnover_rate_purchase /mnt/extra-addons/stock_turnover_rate_purchase
COPY stock_warehouse_access /mnt/extra-addons/stock_warehouse_access
COPY stock_warehouse_distance /mnt/extra-addons/stock_warehouse_distance

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
