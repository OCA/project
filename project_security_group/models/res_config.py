# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models
from openerp.osv import fields
from openerp.tools.safe_eval import safe_eval


class ProjectTeamRoleSettings(models.TransientModel):
    _name = 'project.config.settings'
    _inherit = ['project.config.settings']

    _columns = {
        'limit_project_user': fields.boolean(
            string='Limit project users',
            help="Limit project user to see only the task and issue he/she is "
                 "assigned and not all the task of a project. If project user "
                 "is a team member then has permission to see all tasks and "
                 "issues of a project."),
        'only_team_user': fields.boolean(
            string='Limit assign task to members',
            help="Limit the users that can be assigned to a Task to "
                 "the team members"),
    }

    def get_default_limit_project_user(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'limit_project_user': safe_eval(icp.get_param(
                cr, uid, 'project_security_group.limit_project_user', 'False'))
        }

    def get_default_only_team_user(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {'only_team_user': safe_eval(
            icp.get_param(
                cr, uid, 'project_security_group.only_team_user', 'False'))}

    def set_limit_project_user(self, cr, uid, ids, context=None):
        model_obj = self.pool.get('ir.model.data')
        rule_obj = self.pool.get('ir.rule')
        config = self.browse(cr, uid, ids[0], context=context)
        rule_limit_id = model_obj.get_object_reference(
            cr, uid, 'project_security_group',
            'task_limit_project_user_rule')[1]
        rule_default_id = model_obj.get_object_reference(
            cr, uid, 'project', 'task_visibility_rule')[1]
        rule_obj.write(cr, uid, rule_limit_id,
                       {'active': config.limit_project_user})
        rule_obj.write(cr, uid, rule_default_id,
                       {'active': not config.limit_project_user})
        icp = self.pool.get('ir.config_parameter')
        icp.set_param(cr, uid, 'project_security_group.limit_project_user',
                      repr(config.limit_project_user))

    def set_only_team_user(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        icp.set_param(cr, uid, 'project_security_group.only_team_user',
                      repr(config.only_team_user))
