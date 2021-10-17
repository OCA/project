from odoo import fields, models, api


class ProjectTaskState(models.Model):
    _inherit = "project.task"

    pr_state = fields.Selection(
        selection=lambda self: self._selection_pr_state(),
        string="PR State",
        )

    @api.model
    def _selection_pr_state(self):
        """Function to select the state of the pull request"""
        return [
            ('open', 'Open'),
            ('draft', 'Draft'),
            ('merged', 'Merged'),
            ('closed', 'Closed'),
        ]

    @api.model
    def create(self, vals):
        if vals.get('project_id') and vals.get('pr_uri'):
            self._check_pr_state(vals)
        else:
            vals['pr_state'] = None
        return super(ProjectTaskState, self).create(vals)

    def write(self, vals):
        self._check_pr_state(vals)
        return super(ProjectTaskState, self).write(vals)

    def _check_pr_state(self, vals):
        if 'project_id' in vals:
            search_pr_state = self.env['project.project'].search(
                [('id', '=', vals['project_id'])]).pr_state_default
            vals['pr_state'] = search_pr_state
        elif 'pr_uri' in vals:
            if not vals['pr_uri']:
                vals['pr_state'] = None
            else:
                vals['pr_state'] = self.project_id.pr_state_default
