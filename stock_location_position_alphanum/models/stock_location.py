# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    posx = fields.Integer(string='Corridor (X) (Integer)', groups='base.group_no_one')
    posy = fields.Integer(string='Shelves (Y) (Integer)', groups='base.group_no_one')
    posz = fields.Integer(string='Height (Z) (Integer)', groups='base.group_no_one')

    posx_alphanum = fields.Char('Corridor (X)')
    posy_alphanum = fields.Char('Shelves (Y)')
    posz_alphanum = fields.Char('Height (Z)')
