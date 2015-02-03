#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    CopyLeft 2012 - http://www.grupoaltegra.com
#    You are free to share, copy, distribute, transmit, adapt and use for commercial purpose
#    More information about license: http://www.gnu.org/licenses/agpl.html
#    info (moyblanco22@gmail.com)
#
#############################################################################
#
#    Coded by: Carlos Blanco (moyblanco22@gmail.com)
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

from openerp.osv import osv ,fields
from openerp.tools.translate import _

class print_product_purchase(osv.TransientModel):
    _name = 'print.product.purchase'
    
    def action_create_labels(self,cr,uid,ids,context=None):
        """ Crea las etiquetas de los productos comprados recientemente  """
        if context is None:
            context = {}
        # Objetos
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        product_ids = self.pool.get('product.product').search(cr, uid, [('purchased','=',True)])
        if product_ids:
            context.update({'active_ids':product_ids})
            self.pool.get('product.product').write(cr, uid, product_ids, {'purchased':False})
            return self.pool['report'].get_action(cr, uid, product_ids, 'product.product.label', context=context)
        raise osv.except_osv(_('Aviso'),
                        _('No existen productos para imprimir etiquetas.'))
        return {}
