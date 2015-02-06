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
from openerp.tools.translate import _
import time

class arrival_expenses(osv.Model):
    _name = 'arrival.expenses'
    
    
    _columns = {
        'name': fields.char('Proveedor', size=128, required=True, help='Nombre del proveedor en el XMl.'),
        'number': fields.char('Numero de Factura', size=64, required=True, help='Numero de la factura agregada.'),
        'date_invoice': fields.datetime('Fecha de Factura', required=True, help='Fecha de la factura agregada.'),
        'amount_total': fields.float('Monto Total', required=True, help='Monto total de la factura.'),
        'amount_subtotal': fields.float('Subtotal', required=True, help='Monto sin IVA de la factura.'),
        'amount_tax': fields.float('Impuesto', required=True, help='Monto de impuesto de la factura.'),
        'tax': fields.boolean('IVA', help='Indica si esta factura se considero con IVA o sin él.'),
        'arrival_expenses_line_ids': fields.one2many('arrival.expenses.line','arrival_expenses_id'),
        'import_id': fields.many2one('purchase.import', 'Importacion'),
        'ir_attachment_id': fields.many2one('ir.attachment', 'Adjunto'),
        'currency_id': fields.many2one('res.currency', 'Moneda', readonly=True),
    }
    
    _defaults = {
        'tax':True,
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for expenses_row in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in expenses_row.arrival_expenses_line_ids]
            self.pool.get('arrival.expenses.line').unlink(cr, uid, line_ids)
            self.pool.get('ir.attachment').unlink(cr, uid, [expenses_row.ir_attachment_id.id])
        return super(arrival_expenses,self).unlink(cr, uid, ids, context)
    
class arrival_expenses_line(osv.Model):
    _name = 'arrival.expenses.line'
    
    _columns = {
        'name': fields.char('Prodcuto', size=128, required=True, help='Nombre del producto del XML.'),
        'product_qty': fields.float('Cantidad', required=True),
        'price_unit': fields.float('Precio', required=True),
        'arrival_expenses_id': fields.many2one('arrival.expenses', 'Gasto de llegada'),
    }
    
    _defaults = {
    }
    
    
