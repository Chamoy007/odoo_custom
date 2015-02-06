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
from openerp import SUPERUSER_ID, api

class stock_move(osv.Model):
    _inherit = 'stock.move'
    
    def product_price_update_before_done(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        tmpl_dict = {}
        for move in self.browse(cr, uid, ids, context=context):
            #adapt standard price on incomming moves if the product cost_method is 'average'
            if (move.location_id.usage == 'supplier') and (move.product_id.cost_method == 'average'):
                product = move.product_id
                prod_tmpl_id = move.product_id.product_tmpl_id.id
                qty_available = move.product_id.product_tmpl_id.qty_available
                if tmpl_dict.get(prod_tmpl_id):
                    product_avail = qty_available + tmpl_dict[prod_tmpl_id]
                else:
                    tmpl_dict[prod_tmpl_id] = 0
                    product_avail = qty_available
                if product_avail <= 0:
                    if move.purchase_line_id:
                        self.pool.get('purchase.order.line').write(cr, uid, [move.purchase_line_id.id], {'product_standard_price':move.product_id.standard_price,'product_qty_before_incoming':move.product_id.product_tmpl_id.qty_available})
                        if move.purchase_line_id.order_id.type == 'imported':
                            new_std_price = move.purchase_line_id.price_unit_real
                        else:
                            new_std_price = move.price_unit
                    else:
                        new_std_price = move.price_unit
                else:
                    # Get the standard price
                    amount_unit = product.standard_price
                    # Validamos si la entrada proviene de una compra y si la compra es importada o nacional
                    if move.purchase_line_id:
                        self.pool.get('purchase.order.line').write(cr, uid, [move.purchase_line_id.id], {'product_standard_price':move.product_id.standard_price,'product_qty_before_incoming':move.product_id.product_tmpl_id.qty_available})
                        # Si la compra es importada se realiza el calculo del costo medio con el costo real del prodcuto
                        if move.purchase_line_id.order_id.type == 'imported':
                            new_std_price = ((amount_unit * product_avail) + (move.purchase_line_id.price_unit_real * move.product_qty)) / (product_avail + move.product_qty)
                        else:
                            new_std_price = ((amount_unit * product_avail) + (move.price_unit * move.product_qty)) / (product_avail + move.product_qty)
                    else:
                        new_std_price = ((amount_unit * product_avail) + (move.price_unit * move.product_qty)) / (product_avail + move.product_qty)
                tmpl_dict[prod_tmpl_id] += move.product_qty
                # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
                product_obj.write(cr, SUPERUSER_ID, [product.id], {'standard_price': new_std_price}, context=context)
            elif (move.location_id.usage == 'supplier') and (move.purchase_line_id):
                #adapt standard price on incomming moves if the product cost_method is 'average'
                self.pool.get('purchase.order.line').write(cr, uid, [move.purchase_line_id.id], {'product_standard_price':move.product_id.standard_price,'product_qty_before_incoming':move.product_id.product_tmpl_id.qty_available})
