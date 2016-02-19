# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval
from openerp.osv.orm import setup_modifiers
from lxml import etree


class Task(models.Model):
    _inherit = "project.task"

    project_members = fields.Many2many(related='project_id.members')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(Task, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and safe_eval(
                self.env['ir.config_parameter'].get_param(
                    'project_security_group.only_team_user', 'False')):
            res['fields'].update(
                {'project_members':
                    {'domain': [],
                     'invisible': 1,
                     'relation': 'res.users',
                     'context': {},
                     'type': 'many2many'}})
            xml_form = etree.fromstring(res['arch'])
            node = etree.Element('field', {'name': 'project_members'})
            setup_modifiers(node, res['fields']['project_members'])
            placeholder = xml_form.xpath("//field[@name='project_id']")
            placeholder[0].addnext(node)
            res['arch'] = etree.tostring(xml_form)

            domain = "[('id', 'in', project_members[0][2])]"
            res['fields']['user_id']['domain'] = domain
        return res
