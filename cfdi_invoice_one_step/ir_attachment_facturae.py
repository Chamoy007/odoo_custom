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
from openerp.addons.l10n_mx_facturae_lib import facturae_lib
from openerp import netsvc
import base64
import time

class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'
    
    def signal_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if msj:
            raise osv.except_osv(_('Warning'),_(msj))
        #~ try:
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        invoice_obj = self.pool.get('account.invoice')
        attach = ''
        msj = ''
        index_xml = ''
        attach = self.browse(cr, uid, ids[0])
        invoice = attach.invoice_id
        type = attach.type
        wf_service = netsvc.LocalService("workflow")
        save_attach = None
        if 'cbb' in type:
            msj = _("Confirmed")
            save_attach = False
        elif 'cfdi' in type:
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '_V3_2.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, [invoice.id], context=context)
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=None)
            msj = _("Attached Successfully XML CFDI 3.2\n")
            save_attach = True
        elif 'cfd' in type and not 'cfdi' in type:
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, [invoice.id], context=context)
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=None)
            if attach:
                index_xml = self.pool.get('ir.attachment').browse(
                    cr, uid, attach).index_content
                msj = _("Attached Successfully XML CFD 2.2")
            save_attach = True
        else:
            raise osv.except_osv(_("Type Electronic Invoice Unknow!"), _(
                "The Type Electronic Invoice:" + (type or '')))
        if save_attach:
            self.write(cr, uid, ids,
                       {'file_input': attach or False,
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj,
                           'file_xml_sign_index': index_xml}, context=context)
        wf_service.trg_validate(
            uid, self._name, ids[0], 'action_confirm', cr)
        return True
        #~ except Exception, e:
            #~ error = tools.ustr(traceback.format_exc())
            #~ self.write(cr, uid, ids, {'msj': error}, context=context)
            #~ _logger.error(error)
            #~ return False

    def signal_sign(self, cr, uid, ids, context=None):
        #~ try:
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        invoice_obj = self.pool.get('account.invoice')
        attachment_obj = self.pool.get('ir.attachment')
        attach = ''
        index_xml = ''
        msj = ''
        for data in self.browse(cr, uid, ids, context=context):
            invoice = data.invoice_id
            type = data.type
            wf_service = netsvc.LocalService("workflow")
            attach_v3_2 = data.file_input and data.file_input.id or False
            if 'cbb' in type:
                msj = _("Signed")
            if 'cfd' in type and not 'cfdi' in type:
                attach = data.file_input and data.file_input.id or False
                index_xml = data.file_xml_sign_index or False
                msj = _("Attached Successfully XML CFD 2.2\n")
            if 'cfdi' in type:
                # upload file in custom module for pac
                type__fc = self.get_driver_fc_sign()
                if type in type__fc.keys():
                    fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                        '.xml' or ''
                    fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                        cr, uid, [invoice.id], context=context)
                    fdata = base64.encodestring(xml_data)
                    res = type__fc[type](cr, uid, [data.id], fdata, context=context)
                    msj = tools.ustr(res.get('msg', False))
                    index_xml = res.get('cfdi_xml', False)
                    data_attach = {
                        'name': fname_invoice,
                        'datas': base64.encodestring(res.get('cfdi_xml', False)),
                        'datas_fname': fname_invoice,
                        'description': 'Factura-E XML CFD-I SIGN',
                        'res_model': 'account.invoice',
                        'res_id': invoice.id,
                    }
                    # Context, because use a variable type of our code but we
                    # dont need it.
                    attach = attachment_obj.create(cr, uid, data_attach, context=None)
                    if attach_v3_2:
                        cr.execute("""UPDATE ir_attachment
                            SET res_id = Null
                            WHERE id = %s""", (attach_v3_2,))
                else:
                    msj += _("Unknow driver for %s" % (type))
            self.write(cr, uid, ids,
                       {'file_xml_sign': attach or False,
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj,
                           'file_xml_sign_index': index_xml}, context=context)
            wf_service.trg_validate(uid, self._name, data.id, 'action_sign', cr)

        return True
            
        #~ except Exception, e:
            #~ error = tools.ustr(traceback.format_exc())
            #~ self.write(cr, uid, ids, {'msj': error}, context=context)
            #~ _logger.error(error)
            #~ return False
    
    
