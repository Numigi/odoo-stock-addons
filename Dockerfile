FROM quay.io/numigi/odoo-public:12.0
MAINTAINER numigi <contact@numigi.com>

USER root

ARG GIT_TOKEN

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY purchase_warehouse_access /mnt/extra-addons/purchase_warehouse_access
COPY stock_inventory_internal_location /mnt/extra-addons/stock_inventory_internal_location
COPY stock_warehouse_access /mnt/extra-addons/stock_warehouse_access

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
