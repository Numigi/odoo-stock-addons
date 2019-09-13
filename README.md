# Stock Addons

This repository contains Odoo addons related to inventory.

## Business Activity Agnostic

These addons must be relevant to more than one vertical business activity (medical, equipment location, construction, etc).

## Application Agnostic

These addons should have very low coupling with the ``Sales`` and ``Purchases`` applications.
The reason is that if your module is specific to ``Sales``, then, this is likely a ``Sales`` module. Idem thing for purchases.

One exeption is the module ``purchase_warehouse_access``. This module is a binding between ``stock_warehouse_access`` and the ``Purchase`` application. Separating these modules in different repositories would make them harder to maintain.
