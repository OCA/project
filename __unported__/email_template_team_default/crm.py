# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Daniel Reis
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
##############################################################################

from osv import fields, osv

#TODO: should be a m2m field instead, defining a template per Model ...
class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _columns = {
        'template_id': fields.many2one('email.template', 'Default email template'),
    }
crm_case_section()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


