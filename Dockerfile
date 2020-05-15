FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

COPY stock_immediate_transfer_disable /mnt/extra-addons/stock_immediate_transfer_disable
COPY stock_move_list_cost /mnt/extra-addons/stock_move_list_cost
COPY stock_move_origin_link /mnt/extra-addons/stock_move_origin_link
COPY stock_picking_show_address /mnt/extra-addons/stock_picking_show_address
COPY stock_previous_step_return /mnt/extra-addons/stock_previous_step_return
COPY stock_product_location_info /mnt/extra-addons/stock_product_location_info

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
