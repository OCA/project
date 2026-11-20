# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import tagged

from .common import TestTaskStageOrderCommon


@tagged("-at_install", "post_install")
class TestTaskStageOrder(TestTaskStageOrderCommon):
    def test_sequence_rows_created_on_stage_creation(self):
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertTrue(row_a)
        self.assertTrue(row_b)

    def test_reorder_within_project_is_isolated(self):
        self.stage_new.with_context(default_project_id=self.project_a.id).write(
            {"sequence": 50}
        )
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertEqual(row_a.sequence, 50)
        self.assertNotEqual(row_b.sequence, 50)
        self.assertNotEqual(self.stage_new.sequence, 50)

    def test_reorder_from_configuration_pushes_to_all_projects(self):
        self.stage_new.write({"sequence": 80})
        row_a = self._sequence_for(self.project_a, self.stage_new)
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertEqual(row_a.sequence, 80)
        self.assertEqual(row_b.sequence, 80)

    def test_create_duplicate_name_merges_into_existing_stage(self):
        project_c = self._create_project(name="Test Project C")
        count_before = self.Stage.search_count([("name", "=", "Test New Stage")])
        self.Stage.create(
            {
                "name": "Test New Stage",
                "project_ids": [(6, 0, [project_c.id])],
            }
        )
        count_after = self.Stage.search_count([("name", "=", "Test New Stage")])
        self.assertEqual(count_before, count_after)
        self.assertIn(project_c, self.stage_new.project_ids)

    def test_unlink_blocked_when_tasks_exist(self):
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_a.id,
                "stage_id": self.stage_new.id,
            }
        )
        row = self._sequence_for(self.project_a, self.stage_new)
        with self.assertRaises(UserError):
            row.unlink()

    def test_unlink_removes_project_and_cleans_up_orphan_stage(self):
        project_only = self._create_project(name="Test Project Only")
        stage_only = self._create_stage(
            name="Test Only Stage",
            project_ids=[(6, 0, [project_only.id])],
        )
        row = self._sequence_for(project_only, stage_only)
        row.unlink()
        self.assertFalse(stage_only.exists())

    def test_stage_unlink_redirects_when_multiple_projects(self):
        self.stage_new.with_context(default_project_id=self.project_a.id).unlink()
        self.assertTrue(self.stage_new.exists())
        self.assertNotIn(self.project_a, self.stage_new.project_ids)
        self.assertIn(self.project_b, self.stage_new.project_ids)

    def test_stage_unlink_deletes_when_only_project(self):
        project_only = self._create_project(name="Test Project Only Delete")
        stage_only = self._create_stage(
            name="Test Solo Stage",
            project_ids=[(6, 0, [project_only.id])],
        )
        stage_only.with_context(default_project_id=project_only.id).unlink()
        self.assertFalse(stage_only.exists())

    def test_stage_unlink_archives_when_tasks_exist(self):
        project_only = self._create_project(name="Test Project With Task")
        stage_only = self._create_stage(
            name="Test Stage With Task",
            project_ids=[(6, 0, [project_only.id])],
        )
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": project_only.id,
                "stage_id": stage_only.id,
            }
        )
        stage_only.with_context(default_project_id=project_only.id).unlink()
        self.assertTrue(stage_only.exists())
        self.assertFalse(stage_only.active)

    def test_removing_project_from_stage_cleans_up_sequence_row(self):
        self.stage_new.write({"project_ids": [(3, self.project_b.id)]})
        row_b = self._sequence_for(self.project_b, self.stage_new)
        self.assertFalse(row_b)
        self.assertNotIn(self.project_b, self.stage_new.project_ids)

    def test_create_sequence_row_directly_links_project_to_stage(self):
        project_d = self._create_project(name="Test Project D")
        self.Sequence.create(
            {
                "project_id": project_d.id,
                "stage_id": self.stage_new.id,
                "sequence": 5,
            }
        )
        self.assertIn(project_d, self.stage_new.project_ids)

    def test_kanban_order_reflects_project_sequence(self):
        self._sequence_for(self.project_a, self.stage_new).sequence = 100
        self._sequence_for(self.project_a, self.stage_done).sequence = 1
        ordered = self.Task.with_context(
            default_project_id=self.project_a.id
        )._read_group_stage_ids(self.stage_new | self.stage_done, [])
        self.assertEqual(list(ordered), [self.stage_done, self.stage_new])

    def test_set_values_syncs_task_stage_order(self):
        self.env.company.task_stage_order_enabled = False
        project_e = self._create_project(name="Test Project E")
        self.stage_new.project_ids = [(4, project_e.id)]
        self.assertFalse(self._sequence_for(project_e, self.stage_new))
        settings = self.env["res.config.settings"].create(
            {"task_stage_order_enabled": True}
        )
        settings.set_values()
        self.assertTrue(self._sequence_for(project_e, self.stage_new))

    def test_project_write_type_ids_syncs(self):
        project_e = self._create_project(name="Test Project E")
        project_e.write({"type_ids": [(4, self.stage_new.id)]})
        self.assertTrue(self._sequence_for(project_e, self.stage_new))

    def test_create_respects_disabled_flag(self):
        self.env.company.task_stage_order_enabled = False
        project_f = self._create_project(name="Test Project F")
        stage_f = self._create_stage(
            name="Test Stage F",
            project_ids=[(6, 0, [project_f.id])],
        )
        self.assertFalse(self._sequence_for(project_f, stage_f))

    def test_unlink_without_context_deletes_globally(self):
        project_only = self._create_project(name="Test Project No Context")
        stage_only = self._create_stage(
            name="Test Stage No Context",
            project_ids=[(6, 0, [project_only.id])],
        )
        stage_only.unlink()
        self.assertFalse(stage_only.exists())

    def test_project_create_with_type_ids_syncs(self):
        project_g = self.Project.create(
            {
                "name": "Test Project G",
                "type_ids": [(4, self.stage_new.id)],
            }
        )
        self.assertTrue(self._sequence_for(project_g, self.stage_new))

    def test_task_stage_order_enabled_follows_company_flag(self):
        self.assertTrue(self.project_a.task_stage_order_enabled)
        self.env.company.task_stage_order_enabled = False
        self.project_a.invalidate_recordset(["task_stage_order_enabled"])
        self.assertFalse(self.project_a.task_stage_order_enabled)

    def test_read_group_stage_ids_disabled_returns_standard_order(self):
        self.env.company.task_stage_order_enabled = False
        stages = self.stage_new | self.stage_done
        result = self.Task.with_context(
            default_project_id=self.project_a.id
        )._read_group_stage_ids(stages, [])
        self.assertEqual(result, stages)

    def test_project_write_type_ids_removal_cleans_up_sequence_row(self):
        self.project_a.write({"type_ids": [(3, self.stage_new.id)]})
        self.assertFalse(self._sequence_for(self.project_a, self.stage_new))
        self.assertNotIn(self.project_a, self.stage_new.project_ids)

    def test_project_write_type_ids_removal_blocked_when_tasks_exist(self):
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_a.id,
                "stage_id": self.stage_new.id,
            }
        )
        with self.assertRaises(UserError):
            self.project_a.write({"type_ids": [(3, self.stage_new.id)]})

    def test_archiving_stage_removes_rows_and_unarchiving_resyncs(self):
        self.stage_new.active = False
        self.assertFalse(self._sequence_for(self.project_a, self.stage_new))
        self.assertFalse(self._sequence_for(self.project_b, self.stage_new))
        self.assertIn(self.project_a, self.stage_new.project_ids)
        self.stage_new.active = True
        self.assertTrue(self._sequence_for(self.project_a, self.stage_new))
        self.assertTrue(self._sequence_for(self.project_b, self.stage_new))

    def test_archiving_stage_with_tasks_does_not_raise(self):
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_a.id,
                "stage_id": self.stage_new.id,
            }
        )
        self.stage_new.active = False
        self.assertFalse(self._sequence_for(self.project_a, self.stage_new))

    def test_read_group_stage_ids_works_for_portal_user(self):
        portal_user = new_test_user(
            self.env, login="portal_user_test", groups="base.group_portal"
        )
        result = (
            self.Task.with_user(portal_user)
            .with_context(default_project_id=self.project_a.id)
            ._read_group_stage_ids(self.stage_new | self.stage_done, [])
        )
        self.assertTrue(result)

    def test_search_read_respects_project_order_for_statusbar(self):
        self._sequence_for(self.project_a, self.stage_new).sequence = 100
        self._sequence_for(self.project_a, self.stage_done).sequence = 1
        result = self.Stage.search_read(
            [("project_ids", "=", self.project_a.id)], ["display_name"]
        )
        ids = [row["id"] for row in result]
        self.assertLess(ids.index(self.stage_done.id), ids.index(self.stage_new.id))

    def test_search_read_ignores_explicit_order(self):
        self._sequence_for(self.project_a, self.stage_new).sequence = 100
        self._sequence_for(self.project_a, self.stage_done).sequence = 1
        result = self.Stage.search_read(
            [("project_ids", "=", self.project_a.id)], ["display_name"], order="id"
        )
        ids = [row["id"] for row in result]
        self.assertEqual(ids, sorted(ids))

    def test_search_read_without_project_domain_unaffected(self):
        result = self.Stage.search_read(
            [("id", "=", self.stage_new.id)], ["display_name"]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.stage_new.id)

    def test_delete_wizard_tasks_count_scoped_to_project(self):
        other_project = self._create_project(name="Test Other Project")
        self.stage_new.project_ids = [(4, other_project.id)]
        self.Task.create(
            {
                "name": "Test Task Other",
                "project_id": other_project.id,
                "stage_id": self.stage_new.id,
            }
        )
        wizard = (
            self.env["project.task.type.delete.wizard"]
            .with_context(default_project_id=self.project_a.id)
            .create({"stage_ids": [(6, 0, [self.stage_new.id])]})
        )
        self.assertEqual(wizard.tasks_count, 0)

    def test_delete_wizard_tasks_count_uses_default_when_disabled(self):
        self.env.company.task_stage_order_enabled = False
        self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_a.id,
                "stage_id": self.stage_new.id,
            }
        )
        wizard = (
            self.env["project.task.type.delete.wizard"]
            .with_context(default_project_id=self.project_a.id)
            .create({"stage_ids": [(6, 0, [self.stage_new.id])]})
        )
        self.assertEqual(wizard.tasks_count, 1)
