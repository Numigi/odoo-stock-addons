# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, _


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcodes.barcode_events_mixin"]

    scan_barcode = fields.Boolean(
        string="Scan from this Operation Type",
        related="picking_type_id.scan_barcode"
    )

    def on_barcode_scanned(self, barcode):
        if not self.scan_barcode or not self.picking_type_id.nomenclature_id:
            return
        else:
            parsed_result = self.picking_type_id.nomenclature_id.parse_barcode(barcode)
            if parsed_result["type"] in ["weight", "product"]:
                if parsed_result["type"] == "weight":
                    product_barcode = parsed_result["base_code"]
                    qty = parsed_result["value"]
                else:  # product
                    product_barcode = parsed_result["code"]
                    qty = 1.0
                product = self.env["product.product"].search(
                    [
                        "|",
                        ("barcode", "=", product_barcode),
                        ("default_code", "=", product_barcode),
                    ],
                    limit=1,
                )
                if product:
                    if not self._check_product(product, qty):
                        return {
                            "warning": {
                                "title": _("Wrong barcode"),
                                "message": _(
                                    'The barcode "%(barcode)s" does not match any '
                                    'product on this picking.'
                                )
                                % {"barcode": product.barcode},
                            }
                        }
                    else:
                        return
        return {
            "warning": {
                "title": _("Wrong barcode"),
                "message": _('The barcode "%(barcode)s" does not match any product.')
                % {"barcode": barcode},
            }
        }

    def _check_product(self, product, qty=1.0):
        """ This method is called when the user scans a product. Its goal
        is to find a candidate move line (or create one, if necessary)
        and process it by incrementing its `qty_done` field with the
        `qty` parameter.
        """
        # Get back the move line to increase. If multiple are found, chose
        # arbitrary the first one that doesn't have qty_done set.
        picking_move_lines = self.move_line_ids_without_package
        if not self.show_reserved:
            picking_move_lines = self.move_line_nosuggest_ids

        corresponding_ml = picking_move_lines.filtered(
            lambda ml: ml.product_id.id == product.id
            and not ml.qty_done
        )[:1]
        if corresponding_ml:
            corresponding_ml.qty_done += qty
            return True
        else:
            return False
