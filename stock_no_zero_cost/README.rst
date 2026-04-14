==================
Stock No Zero Cost
==================

This module ensures the integrity of your inventory valuation by preventing the validation of incoming or internal stock moves with a zero cost.

In Odoo, receiving storable products at 0.00 valuation can significantly corrupt the **Average Cost (AVCO)** or **FIFO** logic, leading to incorrect financial reports and margin analysis. This module acts as a safety guard to ensure every stock entry has a valid financial value.

.. contents:: Table of Contents

Configuration
=============

To allow specific users to bypass the block (e.g., Inventory Managers), you must assign them to the dedicated security group:

1. Go to **Settings > Users & Companies > Users**.
2. Select a user.
3. In the **Access Rights** tab, find the **Inventory** section.
4. Tick the box **"Allow zero cost stock moves"**.

Usage
=====

Standard User (Blocked)
-----------------------
When a user without the bypass right tries to validate a **Receipt**, an **Internal Transfer**, an **Inventory Adjustment**, or a **Manufacturing Order** for a storable product with a 0.00 cost:

* Odoo will display a hard warning message.
* Validation is blocked until the cost is corrected.

Manager User (Bypass with Wizard)
---------------------------------
When an authorized manager validates a move with a 0.00 cost, a confirmation wizard appears:

.. image:: static/description/wizard_warning.png
   :alt: Zero Cost Valuation Warning Wizard

The manager can then:
* **Cancel** to fix the cost.
* **Validate (Force 0 Cost)** to explicitly allow the move.

Audit & Traceability
====================

Every time a zero-cost movement is forced by a manager, the system creates a permanent audit trail:

* **Chatter**: A log note is automatically posted on the document (Picking, MO, or Inventory) with the name of the approver and the timestamp.
* **Stock Move**: The specific note is recorded on the underlying stock moves in the field **"Zero Cost Approval Note"**.

.. image:: static/description/chatter_log.png
   :alt: Chatter Audit Trail

Contributors
============

* The `Numigi <https://numigi.com/r/home>`_ team.