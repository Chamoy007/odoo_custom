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

from openerp.osv import osv, fields

class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    
    def wkf_action_cancel(self, cr, uid, ids, context=None):
        super(purchase_order, self).wkf_action_cancel(cr, uid, ids, context)
        product_ids = []
        for order_row in self.browse(cr, uid, ids, context):
            for line_row in order_row.order_line:
                if line_row.product_id:
                    line_product_confirm_ids = self.pool.get('purchase.order.line').search(cr, uid, [('product_id','=',line_row.product_id.id),('state','=','confirmed')])
                    if not line_product_confirm_ids:
                       if not line_row.product_id.id in product_ids:
                           product_ids.append(line_row.product_id.id)
        if product_ids:
            self.pool.get('product.product').write(cr, uid, product_ids, {'purchased':False})
        return True
    
class purchase_order_line(osv.Model):
    _inherit = 'purchase.order.line'
    
    def action_confirm(self, cr, uid, ids, context=None):
        product_ids = []
        res = super(purchase_order_line, self).action_confirm(cr, uid, ids, context)
        for line_row in self.browse(cr, uid, ids, context):
            if line_row.product_id:
                product_ids.append(line_row.product_id.id)
        if product_ids:
            self.pool.get('product.product').write(cr, uid, product_ids, {'purchased':True})
        return res
