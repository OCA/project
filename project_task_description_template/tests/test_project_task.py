from markupsafe import Markup

from odoo import Command
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.project.tests.test_project_sharing import TestProjectSharingCommon


@tagged("post_install", "-at_install")
class TestDescriptionTemplate(TestProjectSharingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["project.task"]
        cls.Template = cls.env["project.task.description.template"]
        cls.description_template = cls.Template.create(
            {
                "name": "Test Template",
                "description": " - Sample Description",
            }
        )
        cls.template_portal = cls.Template.create(
            {
                "name": "Portal Template",
                "description": "<p>Steps to reproduce</p>",
                "project_ids": [Command.link(cls.project_portal.id)],
            }
        )
        cls.template_cows = cls.Template.create(
            {
                "name": "Cows Template",
                "description": "<p>Cows</p>",
                "project_ids": [Command.link(cls.project_cows.id)],
            }
        )
        cls.template_other = cls.Template.create(
            {
                "name": "Other Template",
                "description": "<p>Other</p>",
                "project_ids": [Command.link(cls.project_no_collabo.id)],
            }
        )

    def test_onchange_description_template_id(self):
        record = self.model.new({"description": "<p>Existing Description</p>"})
        record.description_template_id = self.description_template
        record._onchange_description_template_id()
        self.assertEqual(
            record.description,
            Markup("<p>Existing Description</p><p>- Sample Description</p>"),
            "Onchange method failed to append description correctly.",
        )

    def test_onchange_with_empty_description(self):
        record = self.model.new({})
        record.description_template_id = self.description_template
        record._onchange_description_template_id()
        self.assertEqual(
            record.description,
            Markup("<p>- Sample Description</p>"),
            "Onchange method failed with empty initial description.",
        )

    def test_template_stored(self):
        task = self.model.create(
            {
                "name": "Task",
                "description_template_id": self.description_template.id,
            }
        )
        self.assertEqual(task.description_template_id, self.description_template)

    def test_templates_by_project(self):
        domain = self.model._fields["description_template_id"].domain
        templates = self.Template.search(
            safe_eval(domain, {"project_id": self.project_portal.id})
        )
        self.assertIn(self.template_portal, templates)
        self.assertIn(self.description_template, templates)
        self.assertNotIn(self.template_other, templates)
        self.assertEqual(
            self.project_portal.task_description_template_ids, self.template_portal
        )
        templates = self.Template.search(safe_eval(domain, {"project_id": False}))
        self.assertIn(self.description_template, templates)
        self.assertNotIn(self.template_portal, templates)
