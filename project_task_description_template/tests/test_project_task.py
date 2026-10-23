from markupsafe import Markup

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, tagged
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
        collaborator_vals = {
            "collaborator_ids": [
                Command.create({"partner_id": cls.user_portal.partner_id.id})
            ]
        }
        cls.project_portal.write(
            dict(collaborator_vals, portal_task_description_template_required=True)
        )
        cls.project_cows.write(collaborator_vals)
        cls.project_cows.message_subscribe(partner_ids=cls.user_portal.partner_id.ids)
        cls.PortalTask = (
            cls.env["project.task"]
            .with_user(cls.user_portal)
            .with_context(
                tracking_disable=True, default_project_id=cls.project_portal.id
            )
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
        portal_templates = self.Template.with_user(self.user_portal).search([])
        self.assertEqual(portal_templates, self.template_portal | self.template_cows)

    def test_portal_create_with_template(self):
        with self.get_project_sharing_form_view(self.PortalTask) as form:
            form.name = "Portal issue"
            form.description_template_id = self.template_portal
        self.assertIn("Steps to reproduce", form.record.description)
        self.assertEqual(form.record.description_template_id, self.template_portal)
        with Form(
            self.PortalTask, view="project.project_sharing_quick_create_task_form"
        ) as form:
            form.name = "Portal quick issue"
            form.description_template_id = self.template_portal
        self.assertIn("Steps to reproduce", form.record.description)
        self.assertEqual(form.record.description_template_id, self.template_portal)

    def test_create_without_template(self):
        with self.assertRaises(ValidationError) as error:
            self.PortalTask.create({"name": "Portal issue"})
        self.assertIn(self.project_portal.name, str(error.exception))
        subtask = self.PortalTask.create(
            {"name": "Portal subtask", "parent_id": self.task_portal.id}
        )
        self.assertEqual(subtask.parent_id, self.task_portal)
        subtask = self.PortalTask.with_context(
            default_parent_id=self.task_portal.id
        ).create({"name": "Portal subtask"})
        self.assertEqual(subtask.parent_id, self.task_portal)
        task = self.PortalTask.with_context(
            default_project_id=self.project_cows.id
        ).create({"name": "Portal issue"})
        self.assertEqual(task.project_id, self.project_cows)
        with Form(
            self.PortalTask.with_context(default_project_id=self.project_cows.id),
            view="project.project_sharing_quick_create_task_form",
        ) as form:
            form.name = "Portal quick issue"
        self.assertFalse(form.record.description_template_id)
        task = self.model.with_user(self.user_projectuser).create(
            {"name": "Internal task", "project_id": self.project_portal.id}
        )
        self.assertEqual(task.project_id, self.project_portal)

    def test_portal_edit_without_template(self):
        with self.get_project_sharing_form_view(
            self.task_portal, self.user_portal
        ) as form:
            form.name = "Portal UserTask edited"
        self.assertEqual(self.task_portal.name, "Portal UserTask edited")
        self.assertFalse(self.task_portal.description_template_id)

    def test_portal_template_from_other_project(self):
        with self.assertRaises(ValidationError) as error:
            self.PortalTask.create(
                {
                    "name": "Portal issue",
                    "description_template_id": self.template_cows.id,
                }
            )
        self.assertIn(self.template_cows.name, str(error.exception))
        for template in (self.template_other, self.description_template):
            with self.assertRaises(AccessError):
                self.PortalTask.create(
                    {"name": "Portal issue", "description_template_id": template.id}
                )
        with self.assertRaises(ValidationError) as error:
            self.task_portal.with_user(self.user_portal).write(
                {"description_template_id": self.template_cows.id}
            )
        self.assertIn(self.template_cows.name, str(error.exception))
        task = self.model.with_user(self.user_projectuser).create(
            {
                "name": "Internal task",
                "project_id": self.project_portal.id,
                "description_template_id": self.template_cows.id,
            }
        )
        self.assertEqual(task.description_template_id, self.template_cows)

    def test_required_project_without_templates(self):
        with self.assertRaises(ValidationError) as error:
            self.project_cows.write(
                {
                    "portal_task_description_template_required": True,
                    "task_description_template_ids": [Command.clear()],
                }
            )
        self.assertIn(self.project_cows.name, str(error.exception))
        with self.assertRaises(ValidationError):
            self.project_portal.task_description_template_ids = False
        with self.assertRaises(ValidationError):
            self.template_portal.project_ids = False
        with self.assertRaises(ValidationError):
            self.template_portal.action_archive()
        with self.assertRaises(ValidationError):
            self.template_portal.unlink()
        self.template_cows.project_ids = False
        self.assertFalse(self.project_cows.task_description_template_ids)
        self.project_portal.privacy_visibility = "followers"
        self.template_portal.project_ids = False
        self.assertFalse(self.project_portal.task_description_template_ids)
