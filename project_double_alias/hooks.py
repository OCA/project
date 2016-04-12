# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3).

from openerp import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Change to second alias all the existing project aliases that point to
    issues.
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        alias_obj = env['mail.alias']
        issue_model = env['ir.model'].search([('model', '=', 'project.issue')])
        for project in env['project.project'].search([]):
            if project.alias_model == 'project.issue':
                alias_name = project.alias_name
                project.alias_id.alias_name = False
                project.second_alias_name = alias_name
            else:
                # Search for an existing alias in the system
                alias = alias_obj.search(
                    [('alias_parent_thread_id', '=', project.id),
                     ('alias_model_id', '=', issue_model.id)], limit=1)
                if alias:
                    project.with_context(no_check=True).write({
                        'second_alias_id': alias.id,
                        'second_alias_name': alias.alias_name,
                    })


def uninstall_hook(cr, registry):
    """Restore projects that has only issues alias to the first alias."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        project_obj = env['project.project'].with_context(
            not_force_alias_model=True)
        projects = project_obj.search([('second_alias_id', '!=', False),
                                       ('alias_id.alias_name', '=', False)])
        for project in projects:
            inactive_alias = project.alias_id
            project.write({
                'alias_id': project.second_alias_id.id,
                'alias_model': 'project.issue',
            })
            inactive_alias.unlink()
