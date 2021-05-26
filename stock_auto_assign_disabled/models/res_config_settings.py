from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_reservation_disabled = fields.Selection(
        [
            ("all", "All Product Reservations Disabled"),
            ("serial", "Serialized Product Reservations Disabled"),
        ],
        default="all",
        config_parameter="stock_auto_assign_disabled.config",
    )
