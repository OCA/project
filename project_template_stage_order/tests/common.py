# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestTemplateStageOrderCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.Project = cls.env["project.project"]
        cls.Stage = cls.env["project.task.type"]
        cls.Sequence = cls.env["project.task.type.sequence"]
        cls.Wizard = cls.env["project.template.copy.wizard"]
        cls.LinkWizard = cls.env["project.link.template.wizard"]
        # Setup
        cls.env.company.task_stage_order_enabled = True
        # Instances
        cls.stage_new = cls._create_stage(name="Test New Stage", sequence=1)
        cls.stage_done = cls._create_stage(name="Test Done Stage", sequence=2)
        cls.template = cls._create_project(
            name="Test Template",
            is_template=True,
            type_ids=[(6, 0, [cls.stage_new.id, cls.stage_done.id])],
        )

    @classmethod
    def _create_project(cls, **kwargs):
        return cls.Project.create(kwargs)

    @classmethod
    def _create_stage(cls, **kwargs):
        return cls.Stage.create(kwargs)

    def _sequence_for(self, project, stage):
        return self.Sequence.search(
            [("project_id", "=", project.id), ("stage_id", "=", stage.id)]
        )

    def _copy_template(self, name, link_to_template=False):
        wizard = self.Wizard.create(
            {
                "template_id": self.template.id,
                "name": name,
                "link_to_template": link_to_template,
            }
        )
        result = wizard.action_confirm()
        return self.Project.browse(result["res_id"])
