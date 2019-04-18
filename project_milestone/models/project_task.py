from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    milestone_id = fields.Many2one('project.milestone',
                                   string="Milestones",
                                   group_expand='_read_group_milestone_ids',
                                   domain="[('project_id', '=', project_id)]")
    use_milestones = fields.Boolean(string="Use Milestones",
                                    related='project_id.use_milestones',
                                    help="If enabled, then Milestones will be \
                                          available. Related to the Project \
                                          'Use Milestones' field.")

    @api.model
    def _read_group_milestone_ids(self, milestone_ids, domain, order):
        if 'default_project_id' in self.env.context:
            milestone_ids = self.env['project.milestone'].search([(
                'project_id', '=', self.env.context['default_project_id'])])
        return milestone_ids
