[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.numigi.tech/builds?repo=numigi/odoo-stock-addons&target_branch=14.0)

# Stock Addons

This repository contains Odoo addons related to inventory.

## Business Activity Agnostic

These addons must be relevant to more than one vertical business activity (medical, equipment location, construction, etc).

## Application Agnostic

These addons should have very low coupling with the ``Sales`` and ``Purchases`` applications.
The reason is that if your module is specific to ``Sales``, then, this is likely a ``Sales`` module. Idem thing for purchases.
