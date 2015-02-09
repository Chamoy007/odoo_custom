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
#    Coded by: Eric Hernandez (eric.hernandez@experts.com.mx)
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
    "name" : 'CFDI invoice in two steps',
    "version" : '1.0',
    "author" : 'Experts',
    "category" : 'Custom Modules',
    "website" : "http://experts.com.mx",
    "description" : """ 
            This module add new button by validating the invoice create and sign the XML automatically
                    """,
    "init_xml" : [],
    "depends" : ['base','l10n_mx_facturae_pac'],
    "update_xml" : ['invoice_view.xml',
        ],
    "demo_xml" : [
    ],
    "test" : [
    ],
    "installable" : True,
    "images": [],
    "auto_install" : False,
}
