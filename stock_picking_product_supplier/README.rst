# Stock Picking Product Supplier

This module extends the module `stock`.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributors](#contributors)

## Overview

This module displays the supplier reference of the product on stock move lines during receipts. The supplier reference is retrieved based on the supplier associated with the incoming transfer.

As a user with access to goods receipts, you will notice a new field on stock move lines.

This field is displayed exclusively on transfers of the receipt type and is propagated from the product form under the Purchase tab.

## Configuration

In the form view of a product, the supplier reference can be found under the Purchase tab.

![Product Template Form](stock_picking_product_supplier/static/description/product_template_form.png)

The value defined on the product is displayed on stock move lines during the receipt.

![Picking Form](stock_picking_product_supplier/static/description/picking_form.png)

## Usage

In the form view of a stock move line, the supplier reference of the product is displayed on each line during receipt.

![Purchase Order Form](stock_picking_product_supplier/static/description/purchase_order_form.png)

## Contributors

* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
