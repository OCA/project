from odoo.tests.common import TransactionCase


class TestScopedTagPostInit(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a project, a task, and a tag with old linking logic
        self.project = self.env["project.project"].create({"name": "Demo Project"})
        self.tag = self.env["project.tags"].create({"name": "Legacy Tag"})
        self.task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, [self.tag.id])],
            }
        )
        # Simulate tag is not yet available in available_in_project_ids
        self.tag.available_in_project_ids = [(5, 0, 0)]

    def test_post_init_sets_available_in_project_ids(self):
        from ..hooks import post_init_set_scoped_tags

        post_init_set_scoped_tags(self.env.cr, self.env.registry)
        self.assertIn(self.project, self.tag.available_in_project_ids)
