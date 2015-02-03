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

{
    "name" : 'Products Labels customization ',
    "version" : '0.1',
    "author" : 'Carlos Blanco',
    "category" : 'Custom Modules',
    "website" : "",
    "description" : """ This Module Added name to product labels and create labels for products purchased""",
    "init_xml" : [],
    "depends" : ['base','product','purchase','sale'],
    "update_xml" : [
            'product_report.xml',
            'wizard/print_product_purchase.xml',
        ],
    "demo_xml" : [
    ],
    "test" : [
    ],
    "installable" : True,
    "images": [],
    "auto_install" : False,
}
