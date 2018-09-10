FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

COPY stock_immediate_transfer_disable /mnt/extra-addons/stock_immediate_transfer_disable
COPY stock_picking_show_address /mnt/extra-addons/stock_picking_show_address

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
