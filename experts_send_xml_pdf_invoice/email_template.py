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

import base64
import logging

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import tools
from openerp import netsvc

class email_template(osv.osv):
    _inherit = "email.template"
    
    def generate_email_batch(self, cr, uid, template_id, res_ids, context=None, fields=None):
        invoice_obj = self.pool.get('account.invoice')
        values = super(email_template, self).generate_email_batch(cr, uid, template_id, res_ids, context, fields)
        if context.get('active_model') == 'account.invoice':
            invoice_row = invoice_obj.browse(cr, uid, context.get('active_id'))
            attach_xml_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',context.get('active_id')), ('file_type','=','application/xml'), ('res_model','=','account.invoice'),('datas_fname','like',invoice_row.fname_invoice)], context = context)
            attach_pdf_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',context.get('active_id')), ('file_type','=','application/pdf'), ('res_model','=','account.invoice'),('datas_fname','like',invoice_row.fname_invoice)], context = context)
            if attach_xml_ids:
                values[context.get('active_id')]['attachment_ids'].extend(attach_xml_ids)
            if attach_pdf_ids:
                values[context.get('active_id')]['attachment_ids'].extend(attach_pdf_ids)
        return values
