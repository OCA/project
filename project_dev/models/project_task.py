# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _domain_dev_ids(self):
        return [("id", "in", self.env.ref("project_dev.project_devs_group").users.ids)]

    dev_ids = fields.Many2many(
        "res.users",
        "task_user_rel",
        "task_id",
        "user_id",
        string="Devs",
        domain=_domain_dev_ids,
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group("project_dev.project_devs_group"):
            domain = [("dev_ids", "in", self.env.user.ids)]
            args = args + domain
        return super(ProjectTask, self).search(args, offset, limit, order, count=count)

    @api.model
    def create(self, vals):
        if self.env.context.get("default_parent_id", False):
            parent_task = self.browse(self.env.context.get("default_parent_id"))
            if parent_task.dev_ids:
                vals.update(
                    {
                        "dev_ids": [(6, 0, parent_task.dev_ids.ids)],
                    }
                )
        res = super(ProjectTask, self).create(vals)
        return res

    @api.onchange("parent_id")
    def parent_id_dev_onchange(self):
        if self.parent_id and self.parent_id.dev_ids:
            self.dev_ids = self.parent_id.dev_ids.ids
        else:
            self.dev_ids = False
