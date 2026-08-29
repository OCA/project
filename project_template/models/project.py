# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models

# see _map_tasks_default_values
TASK_DEFAULT_COPY_CONTEXT_KEY = f"{__name__}.task_default_copy_context_key"
TEMPLATE_TASKS_ONLY_CONTEXT_KEY = f"{__name__}.template_tasks_only_context_key"


class Project(models.Model):
    _inherit = "project.project"

    is_template = fields.Boolean(copy=False)
    project_template_id = fields.Many2one(
        "project.project",
        copy=False,
        domain="[('is_template', '=', True)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._add_project_template_defaults(vals)
        projects = super().create(vals_list)
        for project, vals in zip(projects, vals_list, strict=True):
            project._apply_project_template_from_vals(vals)
        return projects

    def create_project_from_template(self):
        """create a project from this template and open the generated project"""
        if " (TEMPLATE)" in self.name:
            new_name = self.name.replace(" (TEMPLATE)", " (COPY)")
        else:
            new_name = self.name + " (COPY)"
        new_project = self.with_context(**self._get_template_copy_context()).copy(
            default={
                "name": new_name,
                "active": True,
                "alias_name": False,
                "is_template": False,
            }
        )

        return {
            "view_mode": "form",
            "res_model": "project.project",
            "target": "current",
            "res_id": new_project.id,
            "type": "ir.actions.act_window",
        }

    @api.onchange("is_template")
    def on_change_is_template(self):
        """align project metadata with the template flag in the form"""
        if self.name:
            if self.is_template:
                if "(TEMPLATE)" not in self.name:
                    self.name = self.name + " (TEMPLATE)"
                if self.user_id:
                    self.user_id = False
                if self.partner_id:
                    self.partner_id = False
                if self.alias_name:
                    self.alias_name = False

            else:
                if " (TEMPLATE)" in self.name:
                    self.name = self.name.replace(" (TEMPLATE)", "")

    def write(self, vals):
        """keep task template flags aligned when a project changes type"""
        projects_to_enable = self._get_projects_to_toggle_task_template(vals, True)
        projects_to_disable = self._get_projects_to_toggle_task_template(vals, False)
        res = super().write(vals)
        projects_to_enable._set_tasks_template(True)
        projects_to_disable._set_tasks_template(False)
        return res

    def map_tasks(self, new_project_id):
        """delegate regular project copies to core and filter template copies"""
        if not self.env.context.get(TEMPLATE_TASKS_ONLY_CONTEXT_KEY):
            return super().map_tasks(new_project_id)
        return self._copy_template_tasks(new_project_id)

    def _get_template_copy_context(self):
        """return context flags used to copy only reusable template tasks"""
        return {
            TASK_DEFAULT_COPY_CONTEXT_KEY: True,
            TEMPLATE_TASKS_ONLY_CONTEXT_KEY: True,
        }

    @api.onchange("project_template_id")
    def _onchange_project_template_id(self):
        if self.project_template_id:
            self.update(self.project_template_id._prepare_project_template_vals())

    def _add_project_template_defaults(self, vals):
        template = self.browse(vals.get("project_template_id"))
        if not template:
            return
        for field_name, value in template._prepare_project_template_vals().items():
            vals.setdefault(field_name, value)

    def _apply_project_template_from_vals(self, vals):
        template = self.project_template_id
        if template and vals.get("project_template_id") and "tasks" not in vals:
            template.with_context(**template._get_template_copy_context()).map_tasks(
                self.id
            )

    def _prepare_project_template_vals(self):
        """prepare project values copied when selecting this project as template"""
        self.ensure_one()
        return {
            "label_tasks": self.label_tasks,
            "privacy_visibility": self.privacy_visibility,
            "allow_milestones": self.allow_milestones,
            "allow_task_dependencies": self.allow_task_dependencies,
            "type_ids": [Command.set(self.type_ids.ids)],
        }

    def _get_projects_to_toggle_task_template(self, vals, is_template):
        if vals.get("is_template") != is_template:
            return self.browse()
        return self.filtered(lambda project: project.is_template != is_template)

    def _set_tasks_template(self, is_template):
        if self:
            self.with_context(active_test=False).task_ids.write(
                {"is_template": is_template}
            )

    def _get_template_tasks_to_copy(self):
        """return root tasks selected as reusable parts of the template project"""
        self.ensure_one()
        return (
            self.env["project.task"]
            .with_context(active_test=False)
            .search(
                [
                    ("project_id", "=", self.id),
                    ("parent_id", "=", False),
                    ("is_template", "=", True),
                ]
            )
        )

    def _get_template_task_copy_defaults(self, project):
        return {
            **self._map_tasks_default_values(project),
            "is_template": False,
            "task_template_id": False,
        }

    def _copy_template_tasks(self, new_project_id):
        """copy only tasks explicitly marked as reusable template tasks"""
        project = self.browse(new_project_id)
        tasks = self._get_template_tasks_to_copy()
        if self.allow_task_dependencies and "task_mapping" not in self.env.context:
            self = self.with_context(task_mapping={})
        new_tasks = tasks.with_context(copy_project=True).copy(
            self._get_template_task_copy_defaults(project)
        )
        subtasks = new_tasks._get_all_subtasks()
        subtasks_not_displayed = subtasks.filtered(
            lambda task: not task.display_in_project
        )
        subtasks.filtered(lambda task: task.project_id == self).write(
            {"project_id": project.id}
        )
        subtasks_not_displayed.write({"display_in_project": False})
        return True
