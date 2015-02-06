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
from openerp import pooler, tools
import logging
_logger = logging.getLogger(__name__)
import traceback

class account_invoice(osv.Model):
    _inherit = "account.invoice"
    
    def create_ir_attachment_facturae(self, cr, uid, ids, context):
        """
        Método para validar la factura y subirla al pac en un solo paso
        """
        if context is None:
            context = {}
        else:
            ctx = context.copy()
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        result = super(account_invoice, self).create_ir_attachment_facturae(cr, uid, ids, ctx)
        #~ print result,"result"
        try:
            attachment_id = result['res_id']
        except:
            attachment_id = False
        if not attachment_id:
            return True        
        # Confirmamos el attachment
        try:
            ir_attach_obj.signal_confirm(cr, uid, [attachment_id], ctx)
        except Exception, e:
            raise osv.except_osv(_("Error al crear XML"), _(e))
        # Firmamos el attachment
        try:
            ir_attach_obj.signal_sign(cr, uid, [attachment_id], ctx)
        except Exception, e:
            raise osv.except_osv(_("Error al firmar XML"), _(e))
        return True
