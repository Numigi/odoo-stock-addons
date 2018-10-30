# Stock Move Origin Link

This module adds the `Source Document` to the list view of stock pickings and stock moves.

![Stock Move List](static/description/stock_move_list.png?raw=true)

The text is clickable if it refers to an object within the supported types.

For example, in the example above, when clicking on `MO/00003`, the user is redirected to the
form view of the production order.

![MRP Production](static/description/mrp_production_form.png?raw=true)

## Stock Pickings

The feature is available for all stock picking list views.
Here is an example with the list view of delivery orders.

![Delivery Order List](static/description/delivery_order_list.png?raw=true)

When clicking on `SO020`, the user is redirected to the sale order.

![Sale Order Form](static/description/sale_order_form.png?raw=true)

## Supported Origin Documents

The module supports the following documents as origin of a stock move:

* Sale Orders
* Purchase Orders
* Manufacturing Orders

However, the module only depends on the `Inventory` app.
It detects automatically whether the `Sales`, `Purchases` and `MRP` apps are installed.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
