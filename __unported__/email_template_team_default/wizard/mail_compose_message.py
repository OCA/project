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
from osv import osv

class mail_compose_message(osv.osv_memory):
    _inherit = 'mail.compose.message'

    def _get_template_id(self, cr, uid, context=None):
        """
        Return Email Template of particular record, as defined in it's Team (section_id).
        """
        res = None
        if context is None:
            context = {}
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        if active_model and active_id:
            model_obj = self.pool.get(active_model)
            record = model_obj.browse(cr, uid, active_id, context=context)
            try:
                res = record.section_id and record.section_id.template_id and record.section_id.template_id.id or None
            except:
                pass
        return res

    
    _defaults = {
        'template_id' : _get_template_id,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
