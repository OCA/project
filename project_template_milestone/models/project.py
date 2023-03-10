# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTemplate(models.Model):
    _inherit = "project.project"

    def create_project_from_template(self):
        self.ensure_one()
        res = super().create_project_from_template()
        project = self.browse(res["res_id"])
        for milestone in self.milestone_ids:
            milestone.copy(default={"project_id": project.id})
        # LINK THE NEWLY CREATED TASKS TO THE NEWLY CREATED MILESTONES
        for new_task_record in project.task_ids:
            for new_milestone_record in project.milestone_ids:
                if new_task_record.milestone_id.name == new_milestone_record.name:
                    new_task_record.milestone_id = new_milestone_record.id
        return res
