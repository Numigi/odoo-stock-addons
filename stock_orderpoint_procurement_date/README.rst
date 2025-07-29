Stock Orderpoint Procurement Date
=================================
This module fixes timezone issue when setting a orderpoint date.

Issue:
------
When triggering an orderpoint, the date will be set to midnight UTC.
This will cause issue with users in timezones UTC-x, as it will display
the date as the day before.

Fix:
----
The fix is backported from odoo new version to reduce the number of impacted users by moving the
orderpoint date from 0.00 to 12.00.

See commit below:
https://github.com/odoo/odoo/commit/b243849b07c59259467f349f64f54603f4123363

Contributors
------------

The `Numigi <https://numigi.com/r/home>`_ team is the contributor to this project. We help Quebec companies implement Odoo and Konvergo ERP.