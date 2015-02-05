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
from xml.dom import minidom
import base64
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID

class purchase_import(osv.Model):
    _name = 'purchase.import'
    
    def _get_default_company(self, cr, uid, context=None):
        """
        Método para obtener por default la empresa del usuario
        """
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('El usuario no tiene una compañia asignada'))
        return company_id
        
    def _get_default_currency_USD(self, cr, uid, context=None):
        """
        Metodo para obtener por default la moneda dedolares
        """
        model,currency_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'USD')
        if not currency_id:
            raise osv.except_osv(_('Error!'), _('No existe la moneda USD'))
        return currency_id
    
    def _get_total_volume(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """
        Funcion para calcular el volumen total de las compras agregadas a la importacion
        """
        if context is None:
            context = {}
        res = {}
        for import_row in self.browse(cr, uid, ids, context=context):
            total_volume = 0.0
            for purchase_row in import_row.purchase_related_ids:
                total_volume += purchase_row.total_volume
            res[import_row.id] = total_volume
        return res
        
    def _get_total_weight(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """
        Funcion para calcular el peso total de las compras agregadas a la importacion
        """
        if context is None:
            context = {}
        res = {}
        for import_row in self.browse(cr, uid, ids, context=context):
            total_weight = 0.0
            for purchase_row in import_row.purchase_related_ids:
                total_weight += purchase_row.total_weight
            res[import_row.id] = total_weight
        return res
    
    _columns = {
        'name': fields.char('Nombre', size=64, required=True, readonly=True, help='Codigo de importacion creado automaticamente por proveedor',copy=False),
        'state': fields.selection([('draft','Borrador'),('estimated','Estimado'),('completed','Completado'),('done','Realizado'),('cancel','Cancelado')]
        , 'Estado', readonly=True,select=True, copy=False),
        'creation_date': fields.datetime('Creado', help='Fecha en que se creo la importación', readonly=True, copy=False),
        'arrival': fields.date('Fehca de llegada', help='Fecha en que llegara el producto'),
        'shipment_type_id': fields.many2one('shipment.type','Tipo de Envio', required=True, help='Tipo de envio de la importación', readonly=True, states={'draft': [('readonly', False)]}),
        'shipment_method': fields.selection([('air','Aereo'),('maritime','Maritimo')], 'Metodo de Envio', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'purchase_related_ids': fields.many2many('purchase.order', 'import_purchase_rel', 'import_id', 'purchase_id', 'Compras Relacionadas', copy=False, help="Compras que tienne relacion con la importación",readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_supplier_ids': fields.many2many('account.invoice', 'import_invoice_rel', 'import_id', 'invoice_id', 'Facturas de Proveedor', readonly=True, states={'draft': [('readonly', False)]}, copy=False, domain=[('type','=','in_invoice')], help="Factura de los gastos de envio desde el pais origen."),
        'custom_supplier_id': fields.many2one('res.partner', 'Aduana', domain=[('supplier', '=', True)], readonly=True, states={'draft': [('readonly', False)]},copy=False),
        'supplier_id': fields.many2one('res.partner', 'Provedor', domain=[('supplier', '=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'amount_expense': fields.float('Monto total de gasto', readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company'),
        'currency_id': fields.many2one('res.currency', 'Moneda', readonly=True),
        'currency_arrival_id': fields.many2one('res.currency', 'Moneda', readonly=True),
        'custom_currency_id': fields.many2one('res.currency', 'Moneda Aduana', readonly=True,copy=True),
        'arrival_expense': fields.float('Gasto de llegada'),
        'voucher_id': fields.many2one('account.voucher', 'Pago', readonly=True,copy=False),
        'arrival_expenses_id': fields.one2many('arrival.expenses', 'import_id', 'Gastos de Llegada'),
        'expenses_total': fields.float('Gastos totales', readonly="1", copy=False),
        'total_volume': fields.function(_get_total_volume, method=True, type='float', string='Volumen Total', store=False,
            help='Volumen total de la compra'),
        'total_weight': fields.function(_get_total_weight, method=True, type='float', string='Peso Total', store=False,
            help='Peso total de la compra'),
        'xml_file':fields.binary('XML',readonly=True, states={'estimated': [('readonly', False)]}),
        'invoice_refund_id': fields.many2one('account.invoice', 'Nota de credito', readonly=True,copy=False),
    }
    
    _defaults = {
        'state': 'draft',
        'shipment_method': 'air',
        'company_id': _get_default_company,
        'creation_date': fields.datetime.now,
        'name':'/',
        'custom_currency_id':_get_default_currency_USD,
        'currency_id':_get_default_currency_USD,
        'currency_arrival_id':_get_default_currency_USD,
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.import') or '/'
        return super(purchase_import, self).create(cr, uid, vals, context)
    
    def _check_uniq_purchase(self,cr,uid,ids,context=None):
        """ Funcion Constaints para identificar si un numero de parte esta repetido """
        # Obtenemos el registro del producto que estamos creando o guardando
        for import_row in self.browse(cr,uid,ids,context=context):
            for purchase_row in import_row.purchase_related_ids:
                query = "SELECT import_id FROM import_purchase_rel WHERE purchase_id =%s;"
                cr.execute(query,(purchase_row.id,))
                import_ids = [row[0] for row in cr.fetchall()]
                if len(import_ids) > 1:
                    return False
        return True
    
    _constraints = [(_check_uniq_purchase,'La compra solo puede tener una importacion.',['purchase_related_ids'])]
    
    def _prepare_invoice(self, cr, uid, import_row, supplier_id, lines, type_invoice='in_invoice', context=None):
        """
        Crea un diccionario con todos los datos para crear la factura
        """
        if context is None:
            context = {}
        supplier_row = self.pool.get('res.partner').browse(cr, uid, supplier_id)
        #~ model,currency_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'MXN')
        # Obtenemos el diario de ventas
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'purchase'), ('company_id', '=', import_row.company_id.id)],
            limit=1)
        # Creamos el diccionario con los datos bsicos de la factura
        invoice_vals = {
            'name': import_row.name or '',
            'origin': import_row.name,
            'type': type_invoice,
            'reference': import_row.name,
            'account_id': supplier_row.property_account_payable.id,
            'partner_id': supplier_row.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': import_row.currency_id.id,
            'comment': '',
            'payment_term': supplier_row.property_supplier_payment_term and supplier_row.property_supplier_payment_term.id or False,
            'fiscal_position': supplier_row.property_account_position and supplier_row.property_account_position.id or False,
            'date_invoice': False,
            'company_id': import_row.company_id.id,
            'user_id': uid,
        }
        return invoice_vals
    
    def _prepare_invoice_line(self, cr, uid, import_row, account_id=False, context=None):
        """
        Se crea el Diccionario para crear la linea de la factura
        """
        res = {}
        if not account_id:
            prop = self.pool.get('ir.property').get(cr, uid,
                    'property_account_expense_categ', 'product.category',
                    context=context)
            account_id = prop and prop.id or False
        # Obtenemos la cantidad y el id de la unidad de medida
        uosqty = 1
        model,uos_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        pu = 0.0
        if uosqty:
            # Se calcula el precio unitario con los decimales correctos
            pu = round(import_row.amount_expense,
                    self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
        
        # Creamos el diccionario para crear la linea de factura
        res = {
            'name': 'Gasto de porte o envío',
            'origin': import_row.name,
            'account_id': account_id,
            'price_unit': pu,
            'quantity': uosqty,
            'discount': 0.0,
            'uos_id': uos_id,
            'product_id': False,
            'invoice_line_tax_id': [(6, 0, [])],
            'account_analytic_id': False,
        }
        return res
    
    def create_invoice(self, cr, uid, ids, context=None):
        """
        Método para crear la factura con el gasto total
        """
        # objetos
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        # Obtnemos el registro de la importacion par validaro el proveedor y el monto
        import_row = self.browse(cr, uid, ids, context)[0]
        if not import_row.supplier_id:
            raise osv.except_osv(_('Error'), _('No se ingreso proveedor para crear la factura.'))
        if import_row.amount_expense <= 0.0:
            raise osv.except_osv(_('Error'), _('El monto no puede ser menor que cero.'))
        if not import_row.currency_id:
            raise osv.except_osv(_('Error'), _('No se ingreso tipo de moneda de la factura.'))
        # Obtenemos los datos para crear la linea de l afactura
        vals_line = self._prepare_invoice_line(cr, uid, import_row, False, context)
        # Creamos la linea de l afactura
        line_id = invoice_line_obj.create(cr, uid, vals_line)
        # Obtenemos los datos para crear la factura
        vals_invoice = self._prepare_invoice( cr, uid, import_row, import_row.supplier_id.id, [line_id], type_invoice='in_invoice' ,context=context)
        # Creamos la factura
        inv_id = invoice_obj.create(cr, uid, vals_invoice)
        # Obtenemos los datos en base al termino de pago para agregarlo a la factura
        data = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], vals_invoice['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            invoice_obj.write(cr, uid, [inv_id], data['value'], context=context)
        # Calculamos el precio de la factura
        invoice_obj.button_compute(cr, uid, [inv_id])
        # Agregamos l afactura a la importacion y limpiamos los campos de proveedor y monto
        self.write(cr, uid, ids, {'invoice_supplier_ids': [(4,inv_id)],'supplier_id': False, 'amount_expense':0.0})
        return True
    
    def create_payment_customs(self, cr, uid, ids, context=None):
        """
        Método para abrir el wizard del pago para la aduana
        """
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        wizard_row = self.browse(cr, uid, ids[0], context=context)
        if not wizard_row.custom_supplier_id:
            raise osv.except_osv(_('Error!'), _('No se selecciono aduana.'))
            
        return {
            'name':_("Realizar Pago"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': wizard_row.custom_currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(wizard_row.custom_supplier_id).id,
                'default_amount': 0.0,
                'default_reference': wizard_row.name,
                'close_after_process': True,
                'invoice_type': False,
                'invoice_id': False,
                'default_type': 'payment',
                'type': 'payment',
                'import_id': wizard_row.id
            }
        }
    
    def get_ref_percentage(self, cr, uid, import_id, purchase_rows, context=None):
        """
        Obtenemos la cantidad que se debe aumentar por linea de compra dependiendo si es Aereo o maritimo
        """
        import_row = self.browse(cr, uid, import_id)
        # Se recorren todas las compras para calcular el % de referencia por linea de compra
        for purchase_row in purchase_rows:
            for line_row in purchase_row.order_line:
                # Se valida si el metodo de envio es Maritimo o arero para realizar el calculo de la referencia
                if import_row.shipment_method == 'air':
                    ref_percentage = round(float(((line_row.product_id.weight / import_row.total_weight) * 100) * line_row.product_qty), 2)
                elif import_row.shipment_method == 'maritime':
                    ref_percentage = round(float(((line_row.product_id.volume / import_row.total_volume) * 100) * line_row.product_qty), 2)
                # Calculamos el costo unitario que se sumara a cada precio de costo de las lineas de comrpa
                unit_cost = round(float(((ref_percentage/line_row.product_qty) * import_row.expenses_total) / 100), 2)
                new_cost = unit_cost + line_row.supplier_product_cost
                # Actualizamos el precio de coste por linea de compra
                self.pool.get('purchase.order.line').write(cr, uid, [line_row.id],{'ref_percentage': ref_percentage, 'unit_cost':unit_cost, 'price_unit':new_cost})
        return True
    
    def calculate_product_cost(self, cr, uid, ids, context=None):
        """
        Calculamos el gastototal de llegada del producto
        """
        # Obtenemos el ID de la moneda de Dolares
        model,currency_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'USD')
        currency_row = self.pool.get('res.currency').browse(cr, uid, currency_id)
        system_rate = round(1 / currency_row.rate, 2)
        # Recorremos las importaciones para hacer el calculo pro importacion
        for import_row in self.browse(cr, uid, ids, context):
            # Se valida que existan Gastos de envio agregados, compras o pago de estimado de llegada agregados a la importacion
            if not import_row.invoice_supplier_ids:
                raise osv.except_osv(_('Error!'), _('No existen Gastos de porte o envio agregados.'))
            if not import_row.voucher_id:
                raise osv.except_osv(_('Error!'), _('No existe pago estimado de llegada.'))
            if not import_row.purchase_related_ids:
                raise osv.except_osv(_('Error!'), _('No existen compras agregadas a la importacion.'))
            expenses_total = 0.0
            # Si se realiza el calculo del costo en estado draft se calcula con los gastos estimados de llegada
            if import_row.state == 'draft':
                # Se recorren las facturas de porte o envio agregadas
                for invoice_row in import_row.invoice_supplier_ids:
                    if invoice_row.state not in ('open','paid'):
                        raise osv.except_osv(_('Error!'), _('Existen facturas de Gastos de porte o envio sin validar.'))
                    if invoice_row.currency_id.id != currency_row.id:
                        expenses_total += float(invoice_row.amount_total/system_rate)
                    else:
                        expenses_total += float(invoice_row.amount_total)
            # Si se realiza el calculo en estado esimado completo o done se realiza el calculo con los montos reales agregados.
            elif import_row.state in ('estimated','completed','done'):
                if not import_row.arrival_expenses_id:
                    raise osv.except_osv(_('Error!'), _('No existen Gastos de Llegada ingresados.'))
                # Se recorren las facturas con montos reales agregados a la importacion
                for expense_row in import_row.arrival_expenses_id:
                    if expense_row.tax:
                        if expense_row.currency_id.id != currency_row.id:
                            expenses_total += float(expense_row.amount_total/system_rate)
                        else:
                            expenses_total += float(expense_row.amount_total)
                    else:
                        if expense_row.currency_id.id != currency_row.id:
                            expenses_total += float(expense_row.amount_subtotal/system_rate)
                        else:
                            expenses_total += float(expense_row.amount_subtotal)
            # Se suma el pago realizado a los gastos
            expenses_total += import_row.voucher_id.amount
            # Se actualiza en al importacion
            self.write(cr, uid, [import_row.id], {'expenses_total':expenses_total})
        return True
    
    def copy_product_cost(self, cr, uid, purchase_ids, context=None):
        """
        Metodo para guardar el costo del proveedor antes de realizar los calculos de gastos por importacion
        """
        for purchase_row in self.pool.get('purchase.order').browse(cr, uid, purchase_ids):
            for line_row in purchase_row.order_line:
                self.pool.get('purchase.order.line').write(cr, uid, [line_row.id],{'supplier_product_cost': line_row.price_unit})
        return True
    
    def action_estimated_cost_calculation(self, cr, uid, ids, context=None):
        """
        Accion para calcular el costo del producto estimado y cambiar el estado de la importacion a estiado
        """
        self.calculate_product_cost(cr, uid, ids, context)
        import_row = self.browse(cr, uid, ids)[0]
        # Obtenemos los ids delas ocmpras relacionadas
        purchase_ids = [purchase_row.id for purchase_row in import_row.purchase_related_ids]
        # Copiamos los costos de las lineas de compra a otro campo de la linea de compra
        self.copy_product_cost(cr, uid, purchase_ids, context)
        # Calculamos el porcentaje de referencia y costo unitario por linea de compra
        self.get_ref_percentage(cr, uid, import_row.id, import_row.purchase_related_ids, context)
        # Validamos las compras relacionadas
        self.pool.get('purchase.order').signal_workflow(cr, uid, purchase_ids, 'purchase_confirm', context=context)
        # Combiamos el estado a estimado
        self.write(cr, uid, ids, {'state':'estimated'})
        return True
    
    def validate_purchase(self, cr, uid, purchase_rows, context=None):
        """
        Se valida si las entrasdas de las compras ya han sido procesadas
        """
        for purchase_row in purchase_rows:
            for picking_row in purchase_row.picking_ids:
                if picking_row.state not in ('done','cancel'):
                    return False
        return True
    
    def update_standard_price(self, cr, uid, purchase_rows, context=None):
        """
        Metodo para actualizar el precio dle producto si este tiene metodo de costeo como medio
        """
        product_obj = self.pool.get('product.product')
        # Serecorren las lienas de las compras para agregar el nuevo costo por linea de proeducto
        for purchase_row in purchase_rows:
            for line_row in purchase_row.order_line:
                if line_row.product_id:
                    # Si el metodo de costeo del producto es Medio lo calculamos
                    if line_row.product_id.cost_method == 'average':
                        new_std_price = ((line_row.product_standard_price * line_row.product_qty_before_incoming) + (line_row.price_unit * line_row.product_qty)) / (line_row.product_qty_before_incoming + line_row.product_qty)
                        # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
                        product_obj.write(cr, SUPERUSER_ID, [line_row.product_id.id], {'standard_price': new_std_price}, context=context)
                    else:
                        # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
                        product_obj.write(cr, SUPERUSER_ID, [line_row.product_id.id], {'standard_price': line_row.price_unit}, context=context)
        return True
    
    def get_invoice_refund(self, cr, uid, ids, context=None):
        """
        Método para crear la nota de credito en base al pago realizado y los gasto de llegada reales
        """
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        import_row = self.browse(cr, uid, ids)[0]
        # Obtenemos el ID de la moneda de Dolares
        model,currency_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'USD')
        currency_row = self.pool.get('res.currency').browse(cr, uid, currency_id)
        system_rate = round(1 / currency_row.rate, 2)
        expenses_total = 0.0
        for expense_row in import_row.arrival_expenses_id:
            if expense_row.currency_id.id != currency_row.id:
                expenses_total += float(expense_row.amount_total/system_rate)
            else:
                expenses_total += float(expense_row.amount_total)
        diff =  import_row.voucher_id.amount - expenses_total
        # Obtenemos los datos para crear la linea de factura
        vals_line = self._prepare_invoice_line(cr, uid, import_row, False, context)
        vals_line.update({'name': 'Diferencia Pago-Gastos Reales','price_unit':diff})
        # Creamos la linea de l afactura
        line_id = invoice_line_obj.create(cr, uid, vals_line)
        # Obtenemos los datos para crear la factura
        vals_invoice = self._prepare_invoice( cr, uid, import_row, import_row.custom_supplier_id.id, [line_id], 'in_refund', context)
        # Creamos la factura
        inv_id = invoice_obj.create(cr, uid, vals_invoice)
        # Obtenemos los datos en base al termino de pago para agregarlo a la factura
        data = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], vals_invoice['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            invoice_obj.write(cr, uid, [inv_id], data['value'], context=context)
        # Calculamos el precio de la factura
        invoice_obj.button_compute(cr, uid, [inv_id])
        # Confirmamos la factura
        invoice_obj.signal_workflow(cr, uid, [inv_id], 'invoice_open', context=context)
        self.write(cr, uid, [import_row.id], {'invoice_refund_id': inv_id})
        return True
        
    def action_real_cost_calculation(self, cr, uid, ids, context=None):
        """
        Accion para calcular el costo del producto real en base a los montos agregados
        y cambiar el estado de la importacion a completado
        """
        import_row = self.browse(cr, uid, ids)[0]
        if not self.validate_purchase(cr, uid, import_row.purchase_related_ids, context):
            raise osv.except_osv(_('Error!'), _('No se han realizado todas las entradas de las compras.'))
        # Calculamos el costo del producto
        self.calculate_product_cost(cr, uid, ids, context)
        # Obtenemos el % de referencia y costo unitario por linea
        self.get_ref_percentage(cr, uid, import_row.id, import_row.purchase_related_ids, context)
        # Se actualiza el precio de coste de los productos con el costo real del producto
        self.update_standard_price(cr, uid,  import_row.purchase_related_ids, context)
        # Realizamos el calculo para generar una Nota de credito para el prveedor si existe diferencia de montos
        self.get_invoice_refund(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'done'})
        return True
        
    def action_import_completed(self, cr, uid, ids, context=None):
        """
        Accion para cambiar el estado de la importacion a Finalizado
        """
        for immport_row in self.browse(cr, uid, ids, context):
            if not immport_row.arrival_expenses_id:
                raise osv.except_osv(_('Error!'), _('No se agrego gastos de llegada.'))
        self.write(cr, uid, ids, {'state':'completed'})
        return True
    
    def cancel_import_draft(self, cr, uid, ids, context=None):
        """Metodo que cancela las facturas de Gasto de porte y el pago de llegada estimado"""
        # Objetos
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        # Registro de la importacion
        import_row = self.browse(cr, uid, ids, context)[0]
        invoice_ids = [invoice_row.id for invoice_row in import_row.invoice_supplier_ids]
        # Si tiene facturas de gasto de porte o envio se ejecuta la funcion para cancelar
        if invoice_ids:
            invoice_obj.signal_workflow(cr, uid, invoice_ids, 'invoice_cancel', context=context)
        # Si tiene creado un pago de estimado de llegada se cancela
        if import_row.voucher_id:
            voucher_obj.cancel_voucher(cr, uid, [import_row.voucher_id.id], context)
        return True
        
    def cancel_import_estimated(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        # Objetos
        purchase_obj = self.pool.get('purchase.order')
        picking_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        context.update({'cancel_procurement':True})
        # Registro de la importacion
        purchase_ids = []
        import_row = self.browse(cr, uid, ids, context)[0]
        for purchase_row in import_row.purchase_related_ids:
            move_ids = [move_row.id for picking_row in purchase_row.picking_ids for move_row in picking_row.move_lines ]
            picking_ids = [picking_row.id for picking_row in purchase_row.picking_ids]
            move_obj.write(cr, uid, move_ids, {'state':'cancel'})
            picking_obj.action_cancel(cr, uid, picking_ids, context)
            purchase_ids.append(purchase_row.id)
            for line_row in purchase_row.order_line:
                self.pool.get('purchase.order.line').write(cr, uid, [line_row.id],{'price_unit': line_row.supplier_product_cost})
                self.pool.get('product.product').write(cr, uid, [line_row.product_id.id],{'standard_price': line_row.product_standard_price})
        purchase_obj.action_cancel(cr, uid, purchase_ids, context)
        purchase_obj.action_cancel_draft(cr, uid, purchase_ids, context)
        # Si tiene facturas de gasto de porte o envio se ejecuta la funcion para cancelar
        if import_row.invoice_refund_id:
            invoice_obj.signal_workflow(cr, uid, [import_row.invoice_refund_id.id], 'invoice_cancel', context=context)
        return True
        
    def action_import_cancel(self, cr, uid, ids, context=None):
        """
        Accion para cambiar el estado de la importacion a Finalizado
        """
        import_row = self.browse(cr, uid, ids, context)[0]
        self.cancel_import_draft(cr, uid, ids, context)
        if import_row.state == 'estimated':
            self.cancel_import_estimated(cr, uid, ids, context)
        elif import_row.state in ('estimated','completed','done'):
            self.cancel_import_estimated(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'cancel','voucher_id':False,'purchase_related_ids':[(6,False,[])],'expenses_total':0.0,'invoice_refund_id':False})
        #~ self.write(cr, uid, ids, {'state':'cancel'})
        return True
        
    def action_import_cancel_draft(self, cr, uid, ids, context=None):
        """
        Accion para cambiar el estado de la importacion a Finalizado
        """
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def read_xml(self, cr, uid, ids, context=None):
        """
        Método para leer el XML y obtener un diccionario para crear la lineas de factura temporales
        """
        # Obtenemos el registro del wizard
        attachment_obj = self.pool.get('ir.attachment')
        xml_row = self.browse(cr, uid, ids, context)[0]
        number = ""
        supplier_name = ""
        date_m = ""
        # Leemos el archivo
        xml_data = base64.decodestring(xml_row.xml_file)
        #~ xml_data = base64.decodestring(xml_row.xml_filexml_row.xml_filexml_row.xml_file)
        dom = minidom.parseString(xml_data)
        comp = dom.getElementsByTagName('cfdi:Comprobante')[0]
        # Comparamos el RFC del XML y del proveedor seleccionado
        transmitter = comp.getElementsByTagName("cfdi:Emisor")[0]
        # Nombre del proveedor
        supplier_name = transmitter.attributes['nombre'].value
        # Obtenemos el key cfdi: Conceptos
        xml_concepts = comp.getElementsByTagName("cfdi:Conceptos")[0]
        xml_tax = comp.getElementsByTagName("cfdi:Impuestos")[0]
        comp_keys = comp.attributes.keys()
        # Obtenemos la fecha de factura
        if 'fecha' in comp_keys:
            date_xml = comp.attributes['fecha'].value
        # Obtenemos la referencia de lafactura
        #~ comp_keys = comp.attributes.keys()
        if 'folio' in comp_keys:
            number = comp.attributes['folio'].value
        total =  comp.attributes['total'].value
        subtotal = comp.attributes['subTotal'].value
        amount_tax = xml_tax.attributes['totalImpuestosTrasladados'].value
        data_attach = {
            'name': number+'-'+supplier_name,
            #~ 'datas': base64.encodestring(res.get('cfdi_xml', False)),
            'datas': xml_row.xml_file,
            'datas_fname': number+'-'+supplier_name,
            'description': 'XML'+ xml_row.name+'-'+number+'-'+supplier_name,
            'file_type': 'application/xml',
            'res_model': 'purchase.import',
            'res_id': xml_row.id,
        }
        attach = attachment_obj.create(cr, uid, data_attach, context)
        supplier_vals = {
            'name': supplier_name,
            'number': number,
            'date_invoice': date_xml, 
            'amount_total': float(total), 
            'amount_subtotal': float(subtotal), 
            'amount_tax': float(amount_tax), 
            'tax': True, 
            'import_id':xml_row.id,
            'ir_attachment_id':attach,
            'currency_id':xml_row.currency_arrival_id.id,
        }
        expenses_id = self.pool.get('arrival.expenses').create(cr, uid, supplier_vals )
        # Para cada concepto lo agregamos a un diccionario
        for lines in xml_concepts.getElementsByTagName("cfdi:Concepto"):
            invoice_line_vals = {
                'product_qty': lines.attributes['cantidad'].value,
                'name': lines.attributes['descripcion'].value,
                'price_unit': lines.attributes['valorUnitario'].value,
                'arrival_expenses_id': expenses_id,
            }
            expenses_line_id = self.pool.get('arrival.expenses.line').create(cr, uid, invoice_line_vals)
        self.write(cr, uid, ids, {'xml_file':False})
        return expenses_id

    def add_xml(self, cr, uid, ids, context=None):
        """
        Método para crear las lineas que se agregaran a la factura
        """
        xml_row = self.browse(cr, uid, ids, context)[0]
        if not xml_row.xml_file:
            raise osv.except_osv(_('Error!'), _('No se selecciono un XML para agregarlo.'))
        # Obtenemos una lista con datos de las lineas de la factura
        invoice_line_data = self.read_xml(cr, uid, ids, context)
        return True

class shipment_type(osv.Model):
    _name = 'shipment.type'
    
    _columns = {
        'name': fields.char('Nombre', size=64, help=''),
        'description': fields.text('Descripcion', help=''),
    }
