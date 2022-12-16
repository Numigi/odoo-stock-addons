# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Component",
    "summary": "Define components on serial numbers",
    "version": "1.0.0",
    "category": "Inventory",
    "author": "Numigi",
    "license": "LGPL-3",
    "depends": ["stock_serial_single_quant"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/stock_picking.xml",
        "views/stock_production_lot.xml",
        "wizard/stock_component_line_add.xml",
        "wizard/stock_component_line_remove.xml",
    ],
    "installable": True,
}
