# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   sale_project for OpenERP                                                  #
#   Copyright (C) 2010-2013 Akretion LDTA (<http://www.akretion.com>)         #
#   Copyright (C) 2013 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv import fields, orm, osv
from openerp.osv.osv import except_osv
from tools.translate import _
from datetime import date, datetime


class project_project(orm.Model):
    _inherit = "project.project"

    def _default_partner_id(self, cr, uid, context={}):
        return context.get('partner_id', False)

    def _default_project_name(self, cr, uid, context={}):
        if context.get('partner_id', False) and context.get('order_name', False):
            partner_name= self.pool['res.partner'].browse(cr, uid,
                                                        [context['partner_id']],
                                                        context)[0].name[:64].encode('utf-8')
            year = datetime.strftime(date.today(), "%Y")
            order_name = context['order_name'].encode('utf-8')
            name = u"%s - %s - %s" % (partner_name, year, order_name)
            return name
        return False

    _columns = {
        'order_ids': fields.one2many('sale.order', 'true_project_id', 'Orders'),
        'id': fields.integer('ID'),
        }

    _defaults = {
        'partner_id': _default_partner_id,
        'name': _default_project_name,
    }

