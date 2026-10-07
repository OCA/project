# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProjectTag(BaseCommon):
    """Views are checked on their combined arch instead of using ``Form``, so
    the tests do not depend on required fields or ``get_view`` overrides added
    by other installed modules.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = cls.env["project.tags"].create({"name": "Test tag"})
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "tags_required": True}
        )
        cls.project_optional = cls.env["project.project"].create(
            {"name": "Test project optional"}
        )

    def _get_arch(self, model, view_xmlid):
        view = self.env.ref(view_xmlid)
        return etree.fromstring(self.env[model].get_view(view.id)["arch"])

    def test_tags_required_related(self):
        task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, self.tag.ids)],
            }
        )
        self.assertTrue(task.tags_required)
        self.project.tags_required = False
        self.assertFalse(task.tags_required)

    def test_task_without_project_tags_not_required(self):
        task = self.env["project.task"].create(
            {"name": "Task", "project_id": self.project_optional.id}
        )
        self.assertFalse(task.tags_required)
        self.assertFalse(task.tag_ids)

    def test_task_views_tags_required_modifier(self):
        for view in ("project.view_task_form2", "project.quick_create_task_form"):
            with self.subTest(view=view):
                tag_nodes = self._get_arch("project.task", view).xpath(
                    "//field[@name='tag_ids'][not(ancestor::list)]"
                )
                self.assertEqual(len(tag_nodes), 1)
                self.assertEqual(tag_nodes[0].get("required"), "tags_required")

    def test_project_form_tags_required_setting(self):
        arch = self._get_arch("project.project", "project.edit_project")
        self.assertTrue(
            arch.xpath(
                "//group[@name='group_tasks_managment']"
                "//setting[@id='tags_required_setting']"
                "/field[@name='tags_required']"
            )
        )

    def test_project_simplified_form_tags(self):
        arch = self._get_arch(
            "project.project", "project.project_project_view_form_simplified"
        )
        self.assertEqual(len(arch.xpath("//field[@name='tag_ids']")), 1)
