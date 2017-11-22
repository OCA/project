from odoo import models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def toggle_active(self):
        if not self.env.context.get('doing_project_toggle_active'):
            # When called directly from Project, delegate to Analytic Account
            return self.analytic_account_id.toggle_active()
        else:
            # When called from the Analytic Account, perform the toggling
            return super(ProjectProject, self).toggle_active()
