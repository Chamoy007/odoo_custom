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

{
    "name" : 'Send XML & PDF files by email on invoice',
    "version" : '1.0',
    "author" : 'Experts',
    "category" : 'Custom Modules',
    "website" : "http://experts.com.mx",
    "description" : """
        [EN]
        This module adds XML to invoice mail template when this file exists.
        If you want send cfd or cfdi invoice you need to create new template adding this pdf report \n\n
        [ES]
        Este módulo agrega el archivo XML a la plantilla de la factura.
        Si se requiere enviar el PDF de la factura CFD o CFDI se requiere crear otra plantilla que tenga como adjunto este archivo, el XML se agregará automáticamente siempre y cuando ya esté generado.
    """,
    "init_xml" : [],
    "depends" : ['account',],
    "update_xml" : [
        'invoice_template_view.xml'
        ],
    "demo_xml" : [
    ],
    "test" : [
    ],
    "installable" : True,
    "images": [],
    "auto_install" : False,
}
