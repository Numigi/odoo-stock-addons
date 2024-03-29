from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_reservation_disabled = fields.Selection(
        [
            ("off", "All Product Reservations Enabled"),
            ("all", "All Product Reservations Disabled"),
            ("serial_lot", "Serialized/Lot Product Reservations Disabled"),
        ],
        default="off",
        required=True,
        config_parameter="stock_auto_assign_disabled.config",
    )
