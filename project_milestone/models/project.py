# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    milestone_ids = fields.One2many(
        "project.milestone", "project_id", string="Milestones", copy=True
    )
    use_milestones = fields.Boolean(help="Does this project use milestones?")

    milestones_required = fields.Boolean()

    @api.onchange("use_milestones")
    def _onchange_use_milestones(self):
        if not self.use_milestones and self.milestones_required:
            self.milestones_required = False

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        project = super(Project, self).copy(default)
        project._link_tasks_to_milestones()
        return project

    def _link_tasks_to_milestones(self):
        for task in self.with_context(active_test=False).task_ids.filtered(
            "milestone_id"
        ):
            task.milestone_id = self._find_equivalent_milestone(task.milestone_id)

    def _find_equivalent_milestone(self, milestone):
        return next(
            (
                m
                for m in self.with_context(active_test=False).milestone_ids
                if m.name == milestone.name
            ),
            None,
        )
