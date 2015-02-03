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
    "name" : 'importation of products.',
    "version" : '0.1',
    "author" : 'Carlos Blanco',
    "category" : 'Modules',
    "website" : "",
    "description" : """ This module manages costs products and expenses by import""",
    "init_xml" : [],
    "depends" : ['base','product','purchase','account','account_voucher'],
    "update_xml" : [
            'security/ir.model.access.csv',
            'security/sequence.xml',
            'wizard/purchase_import_wizard_view.xml',
            'product_view .xml',
            'arrival_expenses_view.xml',
            'purchase_import_view.xml',
            'purchase_view.xml',
        ],
    "demo_xml" : [
    ],
    "test" : [
    ],
    "installable" : True,
    "images": [],
    "auto_install" : False,
}
