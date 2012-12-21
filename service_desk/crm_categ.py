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

from openerp.osv import fields, orm

class crm_case_categ(orm.Model):
    _inherit = 'crm.case.categ'
    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Service Team'),
        'icon': fields.binary('Icon'),
        'act_window_id': fields.many2one('ir.actions.act_window', 'Action'),
        'show_service_desk': fields.boolean('Show in Service Desk'),
    }

    def open_issue_form(self, cr, uid, ids, context=None):

        def get_action_dict(categ_res):
            """Get Category's Action details dict"""
            _obj = self.pool.get('ir.actions.act_window')
            _id = categ_res.act_window_id.id or self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_desk', 'action_newissue_wizard')[1]
            _cols = ['name','view_type','view_mode','res_model','view_id','views','type','search_view_id','target', 'domain', 'context']
            return _obj.read(cr, uid, _id, _cols, context=context)

        def get_categ_section_id(categ_res):
            """Get Category's Team, searching in parents if necessary"""
            #recursively find parent section_id, if hierarchy is installed
            return categ_res.section_id.id or (
                     hasattr(categ_res, 'parent_id')
                     and categ_res.parent_id
                     and get_categ_section_id(categ_res.parent_id)
                   )

        def get_action_addcontext(categ_res):
            """Return Category's context text to use in the Action"""
            return '"default_master_categ_id":%s,"default_section_id":%s' \
                    % (categ_res.id, get_categ_section_id(categ_res) or None)

        def get_action_context(action, addcontext):
            """Get Action Context updated with additional values"""
            if addcontext and ':' in action['context']:
                end = action.get('context', '').rfind('}') or 0
                return {'context': action['context'][:end] + ',' + addcontext + "}"}
            else:
                return {'context': action.get('context')}

        _res = self.browse(cr, uid, ids[0], context=context)
        action = get_action_dict(_res)
        addcontext = get_action_addcontext(_res)
        action.update(get_action_context(action, addcontext))
        action.update({'view_mode': 'form', 'views': None, 'id': None})
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


