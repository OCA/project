import odoo.tests.common as common


class TestProjectTaskCode(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProjectStatus = self.env["project.status"]
        self.status = self.ProjectStatus.create(
            {
                "name": "New Status",
            }
        )

    def _create_project(self):
        project = self.env["project.project"].create(
            {
                "name": "Project 1",
                "project_status": self.status.id,
            }
        )
        return project

    def test_01_project_status(self):
        project = self._create_project()
        self.assertEqual(project.project_status.id, self.status.id)
        statuses = project._read_group_status_ids(
            project.project_status, [], "status_sequence"
        )
        self.assertTrue(len(statuses) >= 1)
