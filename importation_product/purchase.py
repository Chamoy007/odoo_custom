#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    CopyLeft 2012 - http://experts.com.mx
#    You are free to share, copy, distribute, transmit, adapt and use for commercial purpose
#    More information about license: http://www.gnu.org/licenses/agpl.html
#
#############################################################################
#
#    Coded by: Carlos Blanco (carlos.blanco@experts.com.mx)
#
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('import', 'Importacion'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]
    
    def _get_total_volume(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for purchase_row in self.browse(cr, uid, ids, context=context):
            total_volume = 0.0
            for line_row in purchase_row.order_line:
                if line_row.product_id:
                    total_volume += line_row.product_id.volume
            res[purchase_row.id] = total_volume
        return res
        
    def _get_total_weight(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for purchase_row in self.browse(cr, uid, ids, context=context):
            total_weight = 0.0
            for line_row in purchase_row.order_line:
                if line_row.product_id:
                    total_weight += line_row.product_id.weight
            res[purchase_row.id] = total_weight
        return res
        
    def _get_type_purchase(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for purchase_row in self.browse(cr, uid, ids, context=context):
            query = "SELECT import_id FROM import_purchase_rel WHERE purchase_id =%s;"
            cr.execute(query,(purchase_row.id,))
            import_ids = [row[0] for row in cr.fetchall()]
            if import_ids:
                for import_row in self.pool.get('purchase.import').browse(cr, uid, import_ids):
                    if import_row.state != 'cancel':
                        res[purchase_row.id] = 'imported'
                    else:
                        res[purchase_row.id] = 'national'
            else:
                res[purchase_row.id] = 'national'
        return res
        
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
            help="The status of the purchase order or the quotation request. "
               "A request for quotation is a purchase order in a 'Draft' status. "
               "Then the order has to be confirmed by the user, the status switch "
               "to 'Confirmed'. Then the supplier must confirm the order to change "
               "the status to 'Approved'. When the purchase order is paid and "
               "received, the status becomes 'Done'. If a cancel action occurs in "
               "the invoice or in the receipt of goods, the status becomes "
               "in exception.",
            select=True, copy=False),
        'type': fields.function(_get_type_purchase, type='selection', selection=[('national', 'Nacional'), ('imported', 'Importada')], string='Tipo'),
        'import_id': fields.many2one('purchase.import', 'importacion', help="Importación con la que tendra relacion la compra."),
        'total_volume': fields.function(_get_total_volume, method=True, type='float', string='Volumen Total', store=False,
            help='Volumen total de la compra'),
        'total_weight': fields.function(_get_total_weight, method=True, type='float', string='Peso Total', store=False,
            help='Peso total de la compra'),
    }
    
    
    def purchase_import(self, cr, uid, ids, context=None):
        """
        Metodo para seleccionar una importacion
        """
        vals = {
            'purchase_id': ids[0],
        }
        purchase_import_id = self.pool.get("purchase.import.wizard").create(cr, uid, vals, context=context)
        res = {
            'name':("Importacion de Compra"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'purchase.import.wizard',
            'res_id': purchase_import_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }
        return res
        
        
class purchase_order_line(osv.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'volume': fields.related('product_id','volume',type='float',string='Volumen', store=False, readonly=True),
        'weight': fields.related('product_id','weight',type='float',string='Peso', store=False, readonly=True),
        'ref_percentage': fields.float('Porcentaje Referencia', digits_compute=dp.get_precision('Product Unit of Measure')),
        'unit_cost': fields.float('Gasto unitario', digits_compute=dp.get_precision('Product Unit of Measure')),
        'supplier_product_cost': fields.float('Costo de proveedor'),
        'product_standard_price': fields.float('Costo al intrar'),
        'product_qty_before_incoming': fields.float('Cantidad al entrar'),
    }
