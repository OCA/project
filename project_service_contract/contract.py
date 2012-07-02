# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from osv import osv, fields
from tools.translate import _

#####################
# Parameters Tables #
#####################

class contract_line_state(osv.osv):
    _name = "contract.line.state"
    _columns = {
                'name': fields.char('Name', size=64),
                'description': fields.text('Description'),
    }
contract_line_state()

###############
# Main Tables #
###############

class contract_sub_line(osv.osv):
    _name = "contract.sub.line"
    
    def _get_location(self, cr, uid, ids, product_id, arg, context=None):
        result = {}
        stock_obj = self.pool.get('stock.move')
        for sub_contract_line_id in ids:
            location_id = False
            prod_lot_id = self.browse(cr, uid, sub_contract_line_id, context).stock_production_lot_id
            if prod_lot_id:
                move_ids = stock_obj.search(cr, uid, [('prodlot_id', '=', prod_lot_id.id),('state','=','done')], order='location desc', limit=1)
                if move_ids:
                    location_id = stock_obj.browse(cr, uid, move_ids[0], context).location_dest_id.id
            result[sub_contract_line_id] = location_id
        return result
    
    _columns = {
        'name': fields.related('product_id', 'name', type='char', relation='product.product', string='Name', store= True),
        'contract_id': fields.many2one('contract.contract', 'Contract'),
        'product_id': fields.many2one('product.product', 'Product Name'),
        'qty': fields.integer('Quantity'),
        'stock_production_lot_id': fields.many2one('stock.production.lot', 'Serial Number', domain="[('product_id','=',product_id)]"),
        'contract_line_id': fields.many2one('contract.line', 'Contract Line'),
        'current_location': fields.function(_get_location, method=True, type='many2one',relation='stock.location', string='Current Location', store=True),
    }
    _defaults = {
                 'qty': lambda *a:1,
    }
    
contract_sub_line()

class contract_line(osv.osv):
    _name = "contract.line"    
    
    def _get_location(self, cr, uid, ids, product_id, arg, context=None):
        result = {}
        stock_obj = self.pool.get('stock.move')
        for contract_line_id in ids:
            location_id = False
            prod_lot_id = self.browse(cr, uid, contract_line_id, context).stock_production_lot_id
            if prod_lot_id:
                move_ids = stock_obj.search(cr, uid, [('prodlot_id', '=', prod_lot_id.id),('state','=','done')], order='location desc', limit=1)
                if move_ids:
                    location_id = stock_obj.browse(cr, uid, move_ids[0], context).location_dest_id.id
            result[contract_line_id] = location_id
        return result
    
    _columns = {
        'name': fields.related('product_id', 'name', type='char', relation='product.product', string='Name', store=True),
        'contract_id': fields.many2one('contract.contract', 'Contract'),
        'product_id': fields.many2one('product.product', 'Material Name'),
        'stock_production_lot_id': fields.many2one('stock.production.lot', 'Serial Number', domain="[('product_id','=',product_id)]"),
        'sub_contract_line_ids': fields.one2many('contract.sub.line', 'contract_line_id', string='Related Products'),
        'customer_contact_address_id': fields.many2one('res.partner.address', 'Technical contact customer'),
        'start_date': fields.date('Start date'),
        'end_date': fields.date('End date'),
        'current_location': fields.function(_get_location, method=True, type='many2one',relation='stock.location', string='Current Location', store=True),
        'delivery_location_id': fields.many2one('stock.location', 'Delivery Location'),
        'state_id': fields.many2one('contract.line.state', 'State'),
        'attendance_id' : fields.many2one('resource.calendar', 'Working Time'),
        'gti': fields.float('GTI',  digits=(16,2)),
        'gtr': fields.float('GTR',  digits=(16,2)),
        'note': fields.text('Note'),
    }
contract_line()

class contract_contract(osv.osv):
    _inherit = "contract.contract"    
    _columns = {
        'contract_number': fields.char('Contract Number', size=64),
        'contract_version': fields.char('Version', size=64),
        'sale_odrer_id': fields.many2one('sale.order', 'Sale Order'),
        'order_address_id': fields.many2one('res.partner.address', 'Order Address'),        
        'invoice_address_id': fields.many2one('res.partner.address', 'Invoice Address'),
        'line_ids': fields.one2many('contract.line', 'contract_id', 'Contract Line'),
        'salesman_id': fields.many2one('res.users', 'Salesman'),
        'pre_sales_owner_id': fields.many2one('res.users', 'Pre Sales Responsible'),
        'order_date': fields.date('Date order'),
        'invoice_specification': fields.text('Invoice Specification'),
    }   
contract_contract()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


