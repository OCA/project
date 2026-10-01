# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models

from .project import TASK_DEFAULT_COPY_CONTEXT_KEY, TEMPLATE_TASKS_ONLY_CONTEXT_KEY


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_is_template = fields.Boolean(
        related="project_id.is_template", string="Project Is Template"
    )
    is_template = fields.Boolean(copy=False)
    task_template_id = fields.Many2one(
        "project.task",
        copy=False,
        domain="[('is_template', '=', True), "
        "('project_id.is_template', '=', True), ('id', '!=', id)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """set template defaults before create and apply template fields after"""
        for vals in vals_list:
            self._add_is_template_default(vals)
        tasks = super().create(vals_list)
        for task, vals in zip(tasks, vals_list, strict=True):
            task._apply_template_fields_from_vals(vals)
        return tasks

    def write(self, vals):
        """apply template field behavior after the regular write"""
        res = super().write(vals)
        self._apply_template_fields_from_vals(vals)
        return res

    def copy_data(self, default=None):
        """preserve template-specific fields while reusing the core copy flow"""
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for task, vals in zip(self, vals_list, strict=True):
            task._update_template_copy_data(vals, default)
        return vals_list

    def update_date_end(self, stage_id):
        # keep the template task end date during template project copies
        if self.env.context.get(TASK_DEFAULT_COPY_CONTEXT_KEY):
            return {}
        return super().update_date_end(stage_id)

    @api.onchange("project_id")
    def _onchange_project_id_template(self):
        self.is_template = bool(self.project_id.is_template)

    @api.onchange("task_template_id")
    def _onchange_task_template_id(self):
        if self.task_template_id and self._get_task_template_target_project():
            self.child_ids = [
                Command.create(self._prepare_task_template_child_vals(template_child))
                for template_child in self.task_template_id._get_template_children()
            ]

    def _add_is_template_default(self, vals):
        """default task template flag from its project or parent task"""
        if "is_template" in vals:
            return
        project = self.env["project.project"].browse(
            vals.get("project_id") or self.env.context.get("default_project_id")
        )
        parent = self.browse(
            vals.get("parent_id") or self.env.context.get("default_parent_id")
        )
        vals["is_template"] = bool(project.is_template or parent.is_template)

    def _apply_template_fields_from_vals(self, vals):
        """apply behavior attached to template-related values"""
        if self._should_apply_task_template(vals):
            self._apply_task_template()
        if vals.get("is_template") is False:
            self._set_subtasks_template(False)

    def _should_apply_task_template(self, vals):
        return bool(vals.get("task_template_id") and "child_ids" not in vals)

    def _update_template_copy_data(self, vals, default):
        """adapt copied values when copying a project template or task template"""
        if self.env.context.get(TASK_DEFAULT_COPY_CONTEXT_KEY):
            vals["date_end"] = self.date_end
        if self.env.context.get(TEMPLATE_TASKS_ONLY_CONTEXT_KEY):
            vals.update(is_template=False, task_template_id=False)
            vals["child_ids"] = [
                Command.create(child._prepare_template_child_copy_vals(default))
                for child in self._get_template_children()
            ]

    def _get_template_children(self):
        return self.child_ids.filtered(lambda child: child.active and child.is_template)

    def _prepare_template_child_copy_vals(self, default=None):
        """prepare copied values for a child task inside a template tree"""
        self.ensure_one()
        default = {
            **dict(default or {}),
            "depend_on_ids": False,
            "dependent_ids": False,
            "parent_id": False,
            "is_template": False,
            "task_template_id": False,
        }
        return self._copy_as_template_task(default)

    def _copy_as_template_task(self, default=None):
        """copy a task with template filtering enabled for its children"""
        self.ensure_one()
        return self.with_context(
            copy_project=True,
            **{TEMPLATE_TASKS_ONLY_CONTEXT_KEY: True},
        ).copy_data(dict(default or {}))[0]

    def _set_subtasks_template(self, is_template):
        subtasks = self._get_all_subtasks()
        if subtasks:
            subtasks.write({"is_template": is_template})

    def _apply_task_template(self):
        for task in self.filtered("task_template_id"):
            if not task._get_task_template_target_project():
                continue
            task.write(
                {
                    "child_ids": [
                        Command.create(task._prepare_task_template_child_vals(child))
                        for child in task.task_template_id._get_template_children()
                    ]
                }
            )

    def _get_task_template_target_project(self):
        self.ensure_one()
        return (
            self.project_id
            or self.parent_id.project_id
            or self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
        )

    def _set_template_copy_project(self, vals, project_id):
        if not project_id:
            return
        vals["project_id"] = project_id
        for command in vals.get("child_ids", []):
            if command[0] == Command.CREATE:
                self._set_template_copy_project(command[2], project_id)

    def _prepare_task_template_child_vals(self, template_child):
        """prepare child task values created from the selected task template"""
        self.ensure_one()
        project = self._get_task_template_target_project()
        default = {
            "project_id": project.id,
            "display_in_project": False,
            "is_template": False,
            "task_template_id": False,
        }
        vals = template_child._copy_as_template_task(default)
        self._set_template_copy_project(vals, project.id)
        return vals
