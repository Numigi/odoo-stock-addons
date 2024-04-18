# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
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
                    if self._check_product(product, qty):
                        return
        return {
            "warning": {
                "title": _("Wrong barcode"),
                "message": _(
                    'The barcode "%(barcode)s" doesn\'t correspond to a proper product.'
                )
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
        # Filter out the ones processed by `_check_location` and the ones already
        # having a # destination package.
        picking_move_lines = self.move_line_ids_without_package
        if not self.show_reserved:
            picking_move_lines = self.move_line_nosuggest_ids

        corresponding_ml = picking_move_lines.filtered(
            lambda ml: ml.product_id.id == product.id
            and not ml.result_package_id
            and not ml.lots_visible
            and not ml.qty_done
        )[:1]
        if corresponding_ml:
            corresponding_ml.qty_done += qty
        else:
            # If a candidate is not found, we create one here. If the move
            # line we add here is linked to a tracked product, we don't
            # set a `qty_done`: a next scan of this product will open the
            # lots wizard.
            picking_type_lots = (
                self.picking_type_id.use_create_lots
                or self.picking_type_id.use_existing_lots
            )
            new_move_line = self.move_line_ids.new(
                {
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                    "qty_done": (product.tracking == "none" and picking_type_lots)
                    and qty
                    or 0.0,
                    "product_uom_qty": 0.0,
                    "date": fields.datetime.now(),
                }
            )
            if self.show_reserved:
                self.move_line_ids_without_package += new_move_line
            else:
                self.move_line_nosuggest_ids += new_move_line
        return True
