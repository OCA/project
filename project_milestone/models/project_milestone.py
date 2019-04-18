from odoo import models, fields, api


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _order = 'sequence'

    name = fields.Char(string="Title", required=True)
    target_date = fields.Date(
        string="Target Date",
        required=False,
        help="An target for when the Milestone is planned to be complete.")
    progress = fields.Float(
        string="Progress",
        compute="_compute_milestone_progress",
        store=True,
        help="Percentage of Completed Tasks vs Incomplete Tasks.")
    project_id = fields.Many2one('project.project', string="Project")
    project_tasks = fields.One2many('project.task',
                                    'milestone_id',
                                    string="Project Tasks")
    fold = fields.Boolean(string="KanBan Folded?")
    sequence = fields.Integer(string="Sequence")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('project.milestone') or '/'
        vals['sequence'] = seq
        return super(ProjectMilestone, self).create(vals)

    # COMPUTE MILESTONE PROGRESS
    @api.depends('project_tasks.stage_id')
    def _compute_milestone_progress(self):
        total_tasks_count = 0.0
        closed_tasks_count = 0.0
        for record in self:
            for task_record in record.project_tasks:
                total_tasks_count += 1
                if (task_record.stage_id.closed):
                    closed_tasks_count += 1
            if (total_tasks_count > 0):
                record.progress = (
                    closed_tasks_count / total_tasks_count) * 100
            else:
                record.progress = 0.0
