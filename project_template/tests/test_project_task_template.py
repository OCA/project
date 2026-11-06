# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_project = cls.env["project.project"].create(
            {"name": "Template Project", "is_template": True}
        )
        cls.project = cls.env["project.project"].create({"name": "Target Project"})

    def _create_template_task_tree(self):
        """create a reusable template tree with one branch to skip"""
        template_task = self.env["project.task"].create(
            {"name": "Template parent", "project_id": self.template_project.id}
        )
        template_child = self.env["project.task"].create(
            {
                "name": "Template child",
                "project_id": self.template_project.id,
                "parent_id": template_task.id,
                "is_template": True,
            }
        )
        template_grandchild = self.env["project.task"].create(
            {
                "name": "Template grandchild",
                "project_id": self.template_project.id,
                "parent_id": template_child.id,
                "is_template": True,
            }
        )
        skipped_child = self.env["project.task"].create(
            {
                "name": "Skipped child",
                "project_id": self.template_project.id,
                "parent_id": template_task.id,
                "is_template": False,
            }
        )
        # skipped child descendants must not be copied through their parent
        self.env["project.task"].create(
            {
                "name": "Skipped grandchild",
                "project_id": self.template_project.id,
                "parent_id": skipped_child.id,
                "is_template": True,
            }
        )
        return template_task, template_child, template_grandchild, skipped_child

    def test_onchange_project_id_updates_is_template_on_form(self):
        """project onchange updates the task template flag in forms"""
        with Form(self.env["project.task"]) as task_form:
            task_form.name = "Task"
            task_form.project_id = self.template_project
            self.assertTrue(task_form.is_template)
            task_form.project_id = self.project
            self.assertFalse(task_form.is_template)

    def test_onchange_task_template_id_populates_subtasks_on_form(self):
        """task template onchange adds first-level template children in forms"""
        template_task, template_child, _template_grandchild, skipped_child = (
            self._create_template_task_tree()
        )

        with Form(self.env["project.task"]) as task_form:
            task_form.name = "Target task"
            task_form.project_id = self.project
            task_form.task_template_id = template_task
            self.assertEqual(len(task_form.child_ids), 1)
            with task_form.child_ids.edit(0) as child_form:
                self.assertEqual(child_form.name, template_child.name)
                self.assertNotEqual(child_form.name, skipped_child.name)

    def test_is_template_defaults_from_template_project(self):
        """new tasks in template projects become template tasks by default"""
        task = self.env["project.task"].create(
            {"name": "Template task", "project_id": self.template_project.id}
        )
        self.assertTrue(task.is_template)

    def test_is_template_defaults_from_template_parent(self):
        """new subtasks inherit the template flag from their parent task"""
        parent = self.env["project.task"].create(
            {
                "name": "Template parent",
                "project_id": self.project.id,
                "is_template": True,
            }
        )
        child = self.env["project.task"].create(
            {
                "name": "Template child",
                "project_id": self.project.id,
                "parent_id": parent.id,
            }
        )
        self.assertTrue(child.is_template)

    def test_explicit_is_template_value_is_preserved(self):
        """explicit task template values are not overwritten by defaults"""
        task = self.env["project.task"].create(
            {
                "name": "Not reusable",
                "project_id": self.template_project.id,
                "is_template": False,
            }
        )
        self.assertFalse(task.is_template)

    def test_project_template_flag_updates_existing_tasks(self):
        """changing a project template flag updates its existing tasks"""
        project = self.env["project.project"].create({"name": "Future Template"})
        task = self.env["project.task"].create(
            {"name": "Task", "project_id": project.id}
        )
        self.assertFalse(task.is_template)

        project.is_template = True
        self.assertTrue(task.is_template)

        project.is_template = False
        self.assertFalse(task.is_template)

    def test_disabling_template_task_disables_subtasks(self):
        """disabling a template task also disables all its subtasks"""
        parent = self.env["project.task"].create(
            {"name": "Template parent", "project_id": self.template_project.id}
        )
        child = self.env["project.task"].create(
            {
                "name": "Template child",
                "project_id": self.template_project.id,
                "parent_id": parent.id,
            }
        )
        grandchild = self.env["project.task"].create(
            {
                "name": "Template grandchild",
                "project_id": self.template_project.id,
                "parent_id": child.id,
            }
        )

        parent.is_template = False
        self.assertFalse(child.is_template)
        self.assertFalse(grandchild.is_template)

    def test_create_with_task_template_creates_template_subtasks(self):
        """creating with a task template copies only reusable children"""
        template_task, template_child, template_grandchild, skipped_child = (
            self._create_template_task_tree()
        )
        target_task = self.env["project.task"].create(
            {
                "name": "Target task",
                "project_id": self.project.id,
                "task_template_id": template_task.id,
            }
        )

        self.assertEqual(target_task.child_ids.mapped("name"), [template_child.name])
        copied_child = target_task.child_ids
        # recursive reusable children are copied by the server-side create path
        self.assertEqual(
            copied_child.child_ids.mapped("name"), [template_grandchild.name]
        )
        self.assertEqual(copied_child.child_ids.project_id, self.project)
        self.assertNotIn(skipped_child.name, target_task.child_ids.mapped("name"))
        self.assertEqual(copied_child.project_id, self.project)
        self.assertFalse(copied_child.display_in_project)
        self.assertFalse(copied_child.is_template)
        self.assertFalse(copied_child.task_template_id)
        self.assertFalse(copied_child.child_ids.is_template)

    def test_write_task_template_creates_template_subtasks(self):
        """writing a task template copies reusable children"""
        template_task, template_child, _template_grandchild, _skipped_child = (
            self._create_template_task_tree()
        )
        target_task = self.env["project.task"].create(
            {"name": "Target task", "project_id": self.project.id}
        )

        target_task.task_template_id = template_task

        self.assertEqual(target_task.child_ids.mapped("name"), [template_child.name])

    def test_existing_children_are_kept_when_writing_task_template(self):
        """applying a task template appends to existing children"""
        template_task, template_child, _template_grandchild, _skipped_child = (
            self._create_template_task_tree()
        )
        target_task = self.env["project.task"].create(
            {"name": "Target task", "project_id": self.project.id}
        )
        existing_child = self.env["project.task"].create(
            {
                "name": "Existing child",
                "project_id": self.project.id,
                "parent_id": target_task.id,
            }
        )

        target_task.task_template_id = template_task

        self.assertCountEqual(
            target_task.child_ids.mapped("name"),
            [existing_child.name, template_child.name],
        )

    def test_explicit_child_ids_do_not_apply_task_template(self):
        """explicit children prevent automatic template application"""
        template_task, template_child, _template_grandchild, _skipped_child = (
            self._create_template_task_tree()
        )
        created_task = self.env["project.task"].create(
            {
                "name": "Target task",
                "project_id": self.project.id,
                "task_template_id": template_task.id,
                "child_ids": [
                    Command.create(
                        {
                            "name": "Explicit child on create",
                            "project_id": self.project.id,
                        }
                    )
                ],
            }
        )

        self.assertEqual(
            created_task.child_ids.mapped("name"), ["Explicit child on create"]
        )
        self.assertNotIn(template_child.name, created_task.child_ids.mapped("name"))

        written_task = self.env["project.task"].create(
            {"name": "Target task", "project_id": self.project.id}
        )
        written_task.write(
            {
                "task_template_id": template_task.id,
                "child_ids": [
                    Command.create(
                        {
                            "name": "Explicit child on write",
                            "project_id": self.project.id,
                        }
                    )
                ],
            }
        )

        self.assertEqual(
            written_task.child_ids.mapped("name"), ["Explicit child on write"]
        )
        self.assertNotIn(template_child.name, written_task.child_ids.mapped("name"))

    def test_private_task_with_task_template_does_not_create_subtasks(self):
        """private tasks do not receive generated subtasks from templates"""
        template_task, _template_child, _template_grandchild, _skipped_child = (
            self._create_template_task_tree()
        )

        target_task = self.env["project.task"].create(
            {"name": "Private target task", "task_template_id": template_task.id}
        )

        self.assertFalse(target_task.project_id)
        self.assertFalse(target_task.child_ids)
