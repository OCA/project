from odoo import _, api, fields, models


class ProjectTaskMerge(models.TransientModel):
    _name = "project.task.merge"
    _description = "Project Task Merge"

    task_ids = fields.Many2many("project.task", string="Tasks to Merge", required=True)
    user_ids = fields.Many2many("res.users", string="Assignees")
    create_new_task = fields.Boolean(string="Create a new task")
    dst_task_name = fields.Char(string="New task name")
    dst_project_id = fields.Many2one("project.project", string="Destination Project")
    dst_task_id = fields.Many2one("project.task", string="Merge into an existing task")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        selected_task_ids = self.env["project.task"].browse(
            self.env.context.get("active_ids", [])
        )
        if selected_task_ids:
            res.update(
                {
                    "task_ids": [(6, 0, selected_task_ids.ids)],
                    "user_ids": [(6, 0, selected_task_ids.mapped("user_ids").ids)],
                    "dst_project_id": selected_task_ids[0].project_id.id,
                    "dst_task_id": selected_task_ids[0].id,
                }
            )
        return res

    def merge_tasks(self):
        tag_ids = self.task_ids.mapped("tag_ids").ids
        attachment_ids = self.task_ids.mapped("attachment_ids").ids
        values = {
            "description": self._get_merge_description(),
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
        self._subscribe_merged_followers(merged_tasks)
        for task in merged_tasks:
            self._add_message("to", self.dst_task_id.name, task)
            if task.child_ids:
                for child_task in task.child_ids:
                    self._add_message("to", self.dst_task_id.name, child_task)
                task.child_ids.write({"parent_id": self.dst_task_id.id})
        task_names = ", ".join(merged_tasks.mapped("name"))
        self._add_message("from", task_names, self.dst_task_id)
        merged_tasks.write({"active": False})
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[False, "form"]],
            "res_id": self.dst_task_id.id,
        }

    def _get_merge_description(self):
        return "<br/>".join(
            self.task_ids.filtered(lambda t: t.description).mapped(
                lambda task: f"Description from task <b>"
                f"{task.name}</b>:<br/>{task.description}"
            )
        )

    def _subscribe_merged_followers(self, merged_tasks):
        self.dst_task_id.message_subscribe(
            partner_ids=(merged_tasks).mapped("message_partner_ids").ids
        )

    def _add_message(self, way, task_names, task):
        """Send a message post with to advise the project task about the merge.
        :param way : choice between "from" or "to"
        :param task_names : list of project task names to add in the body
        :param task : the task where the message will be posted
        """
        if task.parent_id:
            message = _(f"This project task has been moved {way} {task_names}")
        else:
            message = _(f"This project task has been merged {way} {task_names}")
        task.message_post(
            body=message, message_type="comment", subtype_xmlid="mail.mt_note"
        )
