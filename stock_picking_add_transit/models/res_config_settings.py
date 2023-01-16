from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transit_partner_type = fields.Selection(
        [
            ("third_party", "Third Party"),
            ("warehouse", "Warehouse"),
        ],
        string="Transit Picking Partner Type",
        default="third_party",
        required=True,
        config_parameter="stock_picking_add_transit.transit_partner_type",
    )
