from odoo import _, fields, models


class ProjectTaskMerge(models.TransientModel):
    _name = "project.task.merge"
    _description = "Project Task Merge"

    task_ids = fields.Many2many("project.task", string="Tasks to Merge", required=True)
    user_ids = fields.Many2many("res.users", string="Assignees")
    create_new_task = fields.Boolean("Create a new task")
    dst_task_name = fields.Char("New task name")
    dst_project_id = fields.Many2one("project.project", string="Destination Project")
    dst_task_id = fields.Many2one("project.task", string="Merge into an existing task")

    def merge_tasks(self):
        tag_ids = self.task_ids.mapped("tag_ids").ids
        attachment_ids = self.task_ids.mapped("attachment_ids").ids
        values = {
            "description": self.merge_description(),
            "tag_ids": [(4, tag_id) for tag_id in tag_ids],
            "attachment_ids": [(4, attachment_id) for attachment_id in attachment_ids],
            "user_ids": self.user_ids.ids,
        }
        if self.create_new_task:
            partner_ids = self.task_ids.mapped("partner_id")
            priorities = self.task_ids.mapped("priority")
            values.update(
                {
                    "name": self.dst_task_name,
                    "project_id": self.dst_project_id.id,
                    "partner_id": len(set(partner_ids)) == 1
                    and partner_ids[0].id
                    or False,
                    "priority": len(set(priorities)) == 1 and priorities[0] or False,
                }
            )
            self.dst_task_id = self.env["project.task"].create(values)
        else:
            self.dst_task_id.write(values)
        merged_tasks = self.task_ids - self.dst_task_id
        self._merge_followers(merged_tasks)
        for task in merged_tasks:
            self._add_message("to", self.dst_task_id.name, task)
        task_names = ", ".join(merged_tasks.mapped("name"))
        self._add_message("from", task_names, self.dst_task_id)
        merged_tasks.write({"active": False})
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[False, "form"]],
            "res_id": self.dst_task_id.id,
        }

    def merge_description(self):
        return "<br/>".join(
            self.task_ids.filtered(lambda t: t.description).mapped(
                lambda task: "Description from task <b>%s</b>:<br/>%s"
                % (task.name, task.description)
            )
        )

    def _merge_followers(self, merged_tasks):
        self.dst_task_id.message_subscribe(
            partner_ids=(merged_tasks).mapped("message_partner_ids").ids
        )

    def default_get(self, fields):
        result = super(ProjectTaskMerge, self).default_get(fields)
        selected_tasks = self.env["project.task"].browse(
            self.env.context.get("active_ids", False)
        )
        assigned_tasks = selected_tasks.filtered(lambda task: task.user_ids)
        result.update(
            {
                "task_ids": selected_tasks.ids,
                "user_ids": assigned_tasks
                and assigned_tasks.mapped("user_ids").ids
                or False,
                "dst_project_id": selected_tasks[0].project_id.id,
                "dst_task_id": selected_tasks[0].id,
            }
        )
        return result

    def _add_message(self, way, task_names, task):
        """Send a message post with to advise the project task about the merge.
        :param way : choice between "from" or "to"
        :param task_names : list of project task names to add in the body
        :param task : the task where the message will be posted
        """
        subject = "Merge project task"
        body = _(f"This project task has been merged {way} {task_names}")

        task.message_post(body=body, subject=subject, content_subtype="plaintext")
