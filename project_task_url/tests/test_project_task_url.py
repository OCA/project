# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectTaskUrl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task = cls.env["project.task"].create({"name": "Test Task"})

    def test_clean_url_no_scheme(self):
        url = self.env["project.task.url"].create(
            {"name": "Link", "url_link": "example.com", "task_id": self.task.id}
        )
        self.assertEqual(url.url_link, "http://example.com")

    def test_clean_url_with_scheme(self):
        url = self.env["project.task.url"].create(
            {
                "name": "Link",
                "url_link": "https://example.com",
                "task_id": self.task.id,
            }
        )
        self.assertEqual(url.url_link, "https://example.com")

    def test_clean_url_protocol_relative(self):
        url = self.env["project.task.url"].create(
            {
                "name": "Link",
                "url_link": "//example.com/path",
                "task_id": self.task.id,
            }
        )
        self.assertEqual(url.url_link, "http://example.com/path")

    def test_clean_url_on_write(self):
        url = self.env["project.task.url"].create(
            {
                "name": "Link",
                "url_link": "https://example.com",
                "task_id": self.task.id,
            }
        )
        url.write({"url_link": "example.org"})
        self.assertEqual(url.url_link, "http://example.org")

    def test_write_without_url_link(self):
        url = self.env["project.task.url"].create(
            {
                "name": "Link",
                "url_link": "https://example.com",
                "task_id": self.task.id,
            }
        )
        url.write({"name": "New Name"})
        self.assertEqual(url.url_link, "https://example.com")

    def test_create_without_url_link(self):
        url = self.env["project.task.url"].create(
            {"name": "Link", "task_id": self.task.id}
        )
        self.assertFalse(url.url_link)

    def test_task_url_ids(self):
        url = self.env["project.task.url"].create(
            {"name": "Link", "url_link": "example.com", "task_id": self.task.id}
        )
        self.assertIn(url, self.task.url_ids)
