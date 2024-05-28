# © 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def _get_default_nomenclature(self):
        return self.env.ref(
            "stock_picking_barcode.picking_barcode_nomenclature",
            raise_if_not_found=False
        )

    scan_barcode = fields.Boolean(
        string="Scan from this Operation Type",
        help="""When this box is checked, a new “Scan” field is displayed on
        transfers of this type of operation to allow scanning of a barcode.""",
    )
    nomenclature_id = fields.Many2one(
        "barcode.nomenclature",
        string="Nomenclature",
        default=_get_default_nomenclature,
        help="""This field allows you to choose the Barcodes Nomenclature
        to apply when scanning.""",
    )
