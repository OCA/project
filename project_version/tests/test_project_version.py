from odoo.addons.base.tests.common import BaseCommon


class TestProjectVersion(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.Version = cls.env["project.version"]

        # Created a project
        cls.project = cls.Project.create(
            {
                "name": "Test Project",
            }
        )

        # Created versions
        cls.version1 = cls.Version.create(
            {
                "name": "1.0",
                "project_id": cls.project.id,
            }
        )

        cls.version2 = cls.Version.create(
            {
                "name": "2.0",
                "project_id": cls.project.id,
            }
        )

        # Created a task
        cls.task = cls.Task.create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "version_id": cls.version1.id,
            }
        )

    def test_project_versions_and_task_assignment(self):
        """Checks project versions and task version assignment."""
        self.assertEqual(
            len(self.project.version_ids), 2, "Project should have 2 versions"
        )
        self.assertIn(
            self.version1, self.project.version_ids, "Version 1.0 missing in project"
        )
        self.assertIn(
            self.version2, self.project.version_ids, "Version 2.0 missing in project"
        )
        self.assertEqual(
            self.task.version_id, self.version1, "Task version is incorrect"
        )

    def test_copy_project_and_task_versions(self):
        """Check project and task copy behavior."""
        cloned_project = self.project.copy()
        self.assertTrue(cloned_project.version_ids, "Copied project has no versions")
        self.assertEqual(
            len(cloned_project.version_ids),
            len(self.project.version_ids),
            "Project version count mismatch",
        )
        cloned_task = self.task.copy()
        self.assertEqual(
            cloned_task.version_id, self.task.version_id, "Task version not copied"
        )
