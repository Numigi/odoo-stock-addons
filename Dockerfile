FROM quay.io/numigi/odoo-public:14.latest
MAINTAINER numigi <contact@numigi.com>

USER root

ARG GIT_TOKEN

COPY .docker_files/test-requirements.txt .
RUN pip3 install -r test-requirements.txt

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo


COPY product_category_safe_change /mnt/extra-addons/product_category_safe_change
COPY product_packaging_dimension_decimal /mnt/extra-addons/product_packaging_dimension_decimal
COPY stock_account_visibility /mnt/extra-addons/stock_account_visibility
COPY stock_auto_assign_disabled /mnt/extra-addons/stock_auto_assign_disabled
# COPY stock_auto_assign_disabled_jit /mnt/extra-addons/stock_auto_assign_disabled_jit
COPY stock_change_qty_reason_enhanced /mnt/extra-addons/stock_change_qty_reason_enhanced
COPY stock_immediate_transfer_disable /mnt/extra-addons/stock_immediate_transfer_disable
COPY stock_location_position_alphanum /mnt/extra-addons/stock_location_position_alphanum
COPY stock_move_location_domain_improved /mnt/extra-addons/stock_move_location_domain_improved
COPY stock_move_origin_link /mnt/extra-addons/stock_move_origin_link
COPY stock_move_valuation_adjustment /mnt/extra-addons/stock_move_valuation_adjustment
COPY stock_picking_groupby_parent_affiliate /mnt/extra-addons/stock_picking_groupby_parent_affiliate
COPY stock_picking_responsible_editable /mnt/extra-addons/stock_picking_responsible_editable
COPY stock_picking_secondary_unit_demand /mnt/extra-addons/stock_picking_secondary_unit_demand
COPY stock_picking_show_address /mnt/extra-addons/stock_picking_show_address
COPY stock_picking_split_qty /mnt/extra-addons/stock_picking_split_qty
COPY stock_picking_tracking_reference /mnt/extra-addons/stock_picking_tracking_reference
COPY stock_product_packaging_dimension /mnt/extra-addons/stock_product_packaging_dimension
COPY stock_product_packaging_uom /mnt/extra-addons/stock_product_packaging_uom
COPY stock_production_lot_rma /mnt/extra-addons/stock_production_lot_rma
COPY stock_quant_by_category /mnt/extra-addons/stock_quant_by_category
COPY stock_quant_secondary_unit /mnt/extra-addons/stock_quant_secondary_unit
COPY stock_rental /mnt/extra-addons/stock_rental
COPY stock_replenish_report_secondary_unit /mnt/extra-addons/stock_replenish_report_secondary_unit
COPY stock_route_optimized /mnt/extra-addons/stock_route_optimized
COPY stock_serial_single_quant /mnt/extra-addons/stock_serial_single_quant
COPY stock_special_route /mnt/extra-addons/stock_special_route
COPY stock_turnover_rate /mnt/extra-addons/stock_turnover_rate
COPY stock_turnover_rate_purchase /mnt/extra-addons/stock_turnover_rate_purchase
COPY stock_virtual_adjustment /mnt/extra-addons/stock_virtual_adjustment

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
