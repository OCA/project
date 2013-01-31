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

        def get_categ_section_id(categ_res):
            """Get Category Team, searching parents upward if necessary"""
            return categ_res.section_id.id or (
                    hasattr(categ_res, 'parent_id') and
                    categ_res.parent_id and
                    get_categ_section_id(categ_res.parent_id))

        def get_custom_action_dict(categ_res):
            """Get dict with the custom Action details for a Category
            If none, use the standard Project Issue form."""
            action_id = categ_res.act_window_id.id \
                or self.pool.get('ir.model.data').get_object_reference(
                    cr, uid, 'project_issue', 'project_issue_categ_act0')[1]
            return self.pool.get('ir.actions.act_window')\
                    .read(cr, uid, action_id, context=context)

        def merge_dict_into_text(text, add_dict):
            """Return the text string with the dict contents added to it.
            Ex: `"{'a':1}"` merged with `{'b': 2}` returns `"{'a':1, 'b':2}"`.
            """
            if ':' not in text:
                return str(add_dict)
            else:
                return '{%s, %s}' % (text.strip()[1:-1], str(add_dict)[1:-1])

        obj = self.browse(cr, uid, ids, context=context)[0]
        action = get_custom_action_dict(obj)
        action.update({
            'domain': [('categ_id', 'child_of', obj.id)],
            'context': merge_dict_into_text(
                action.get('context', ''),
                {'default_master_categ_id': obj.id,
                 'default_section_id': get_categ_section_id(obj) or False,
                 'group_by': False,  # remove inherited section_id grouping
                   },
                ),
            })
        ###print "******\n", action['views'], action['view_mode'], action['domain'], action['context']
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
