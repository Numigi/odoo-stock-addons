Stock Routes Product Multico
============================

This module is a fix of Odoo Stock module: multi-company and multi-routes on product

It's a backport of following commit in version 14.0:
https://github.com/odoo/odoo/commit/a6444faa7bf45b14c4ad63a033814ab0d20ba1da

Steps to reproduce:
---------------------

Before installing this module:

- Multi-warehouse + Multi-company setup
- Create Company A with warehouse and 1-step delivery
- Create Company B with warehouse and 1-step delivery
- Switch to Company A: Set Logistics route on product category
  All/Saleable : 1-step delivery
- Switch to Company B: Set Logistics route on product category
  All/Saleable : 1-step delivery
- Switch to Company A, make sure Company B is turned-off
- Create new product and set category to All/Saleable
- Save product

Multi-company error is coming.

.. image:: static/description/odoo_source_code.png

Current behavior:
------------------

User can not open product when category logistic routes has routes from 2 different companies (even though routes are not visible on its own)

Solution
---------

This is due to the field `route_from_categ_ids` which is a related, and
therefore fetched as `sudo` by default:

https://github.com/odoo/odoo/blob/f0330d92b31bdae4637ae0c26f40ee07282ab449/odoo/fields.py#L368

Actually, the field doesn't seem to be useful since it is only used in a
view.


Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)


More information
----------------
* Meet us at https://bit.ly/numigi-com

