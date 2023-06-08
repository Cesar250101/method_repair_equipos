# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OrdenReparación(models.Model):
    _inherit = 'repair.order'
    
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehículo')
    kilometraje = fields.Integer(string='Kilometraje')

    

