# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProjectStatus(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_read_group_status_ids(self):
        Project = self.env["project.project"]
        grouped_projects = Project.read_group([], ["name"], ["project_status"])
        self.assertEqual(len(grouped_projects), 4)
