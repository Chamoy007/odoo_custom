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

class purchase_import_wizard(osv.osv_memory):
    _name = 'purchase.import.wizard'
    
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Compra', help="Compra que se relacionara con la importacion seleccionada."),
        'add_import': fields.selection([('add','Agregar a importacion'),('create','Crear Importacion')], 'Que desea hacer', required=True),
        'import_id': fields.many2one('purchase.import', 'Importacion', domain=[('state','=', 'draft')], help="Importacion a la que se agregara la compra."),
        'shipment_type_id': fields.many2one('shipment.type','Tipo de Envio',  help='Tipo de envio de la importación'),
    }
    
    _defaults = {
        'add_import': 'create',
    }
    
    def default_get(self, cr, uid, fields, context=None):
        """
        """
        res = super(purchase_import_wizard, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            res.update({'purchase_id':  context.get('active_id')})
        return res
    
    def prepare_purchase_import(self, cr, uid, wizard_row, context=None):
        vals = {
            'shipment_type_id': wizard_row.shipment_type_id.id,
            'purchase_related_ids': [(4,wizard_row.purchase_id.id)]
        }
        return vals
    
    def purchase_import(self, cr, uid, ids, context=None):
        """
        Metodo para seleccionar una importacion
        """
        wizard_row = self.browse(cr, uid, ids)[0]
        if wizard_row.add_import == 'add':
            self.pool.get('purchase.import').write(cr, uid, [wizard_row.import_id.id], {'purchase_related_ids': [(4,wizard_row.purchase_id.id)]})
            import_id = wizard_row.import_id.id
        elif wizard_row.add_import == 'create':
            import_id = self.pool.get('purchase.import').create(cr, uid, self.prepare_purchase_import(cr, uid, wizard_row, context), context)
        return import_id
        
