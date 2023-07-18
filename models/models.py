# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class OrdenReparación(models.Model):
    _inherit = 'repair.order'
    
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehículo')
    kilometraje = fields.Integer(string='Kilometraje')
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Picking')

    
    @api.multi
    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for repair in self:
            # Try to create move with the appropriate owner
            owner_id = False
            available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id, repair.lot_id, owner_id=repair.partner_id, strict=True)
            if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
                owner_id = repair.partner_id.id

            moves = self.env['stock.move']
            picking = self.env['stock.picking']

            tipo_operacion=self.env['stock.picking.type'].search([('es_reparacion','=',True)],limit=1)
            if tipo_operacion:
                pick=picking.create({
                        'picking_type_id': tipo_operacion.id,
                        'partner_id': self.partner_id.id,
                        'origin': self.name,
                        'location_dest_id': tipo_operacion.default_location_dest_id.id,
                        'location_id': tipo_operacion.default_location_src_id.id

                })
                self.picking_id=pick.id
                
            else:
                raise UserError(_("No se ha definido el tipo de operación REPARCION en inventario!"))

            if pick:
                for operation in repair.operations:
                    move = Move.create({
                        'picking_id':pick.id,
                        'name': repair.name,
                        'product_id': operation.product_id.id,
                        'product_uom_qty': operation.product_uom_qty,
                        'product_uom': operation.product_uom.id,
                        'partner_id': repair.address_id.id,
                        'location_id': operation.location_id.id,
                        'location_dest_id': operation.location_dest_id.id,
                        'move_line_ids': [(0, 0, {'product_id': operation.product_id.id,
                                            'lot_id': operation.lot_id.id, 
                                            'product_uom_qty': 0,  # bypass reservation here
                                            'product_uom_id': operation.product_uom.id,
                                            'qty_done': operation.product_uom_qty,
                                            'package_id': False,
                                            'result_package_id': False,
                                            'owner_id': owner_id,
                                            'location_id': operation.location_id.id, #TODO: owner stuff
                                            'location_dest_id': operation.location_dest_id.id,})],
                        'repair_id': repair.id,
                        'origin': repair.name,
                    })
                    moves |= move
                    operation.write({'move_id': move.id, 'state': 'done'})
                vals={
                    'name': repair.name,
                    'picking_id':pick.id,
                    'product_id': repair.product_id.id,
                    'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                    'product_uom_qty': repair.product_qty,
                    'partner_id': repair.address_id.id,
                    'location_id': repair.location_id.id,
                    'location_dest_id': repair.location_id.id,
                    'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                                            'lot_id': repair.lot_id.id, 
                                            'product_uom_qty': 0,  # bypass reservation here
                                            'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                                            'qty_done': repair.product_qty,
                                            'package_id': False,
                                            'result_package_id': False,
                                            'owner_id': owner_id,
                                            'location_id': repair.location_id.id, #TODO: owner stuff
                                            'location_dest_id': repair.location_id.id,})],
                    'repair_id': repair.id,
                    'origin': repair.name,
                }
                move = Move.create(vals)
                consumed_lines = moves.mapped('move_line_ids')
                produced_lines = move.move_line_ids
                moves |= move
                try:
                    moves._action_done()
                except:
                    pass
                produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
                res[repair.id] = move.id
                
            return res

class OrdenReparación(models.Model):
    _inherit = 'stock.picking.type'

    es_reparacion = fields.Boolean(string='Es reparación?')

    @api.onchange('es_reparacion')
    def _onchange_(self):
        self.code='outgoing'

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        self.mapped('purchase_line_id').sudo()._update_received_qty()
        return res