# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.department'

    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
    )

