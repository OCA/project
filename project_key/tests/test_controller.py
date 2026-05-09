# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from .test_common import HttpTestCommon


class TestController(HttpTestCommon):
    def test_01_project_browse(self):
        self.authenticate("admin", "admin")
        response = self.url_open("/projects/" + self.project_1.key)
        self.assertEqual(response.status_code, 200)
        self.assertIn("/web#", response.url)
        self.assertIn(f"model={self.project_1._name}", response.url)
        self.assertIn(f"id={self.project_1.id}", response.url)

    def test_02_task_browse(self):
        self.authenticate("admin", "admin")
        response = self.url_open("/tasks/" + self.task11.key)
        self.assertEqual(response.status_code, 200)
        self.assertIn("/web#", response.url)
        self.assertIn(f"model={self.task11._name}", response.url)
        self.assertIn(f"id={self.task11.id}", response.url)

    def test_03_project_browse_portal(self):
        self.authenticate("portal", "portal")
        response = self.url_open("/projects/" + self.project_1.key)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(f"/my/projects/{self.project_1.id}", response.url)

    def test_04_task_browse_portal(self):
        portal_partner = self.env.ref("base.demo_user0").partner_id
        self.authenticate("portal", "portal")
        project = self.task11.project_id
        self.assertEqual(project.privacy_visibility, "portal")
        self.assertNotIn(project.message_partner_ids, portal_partner)
        response = self.url_open("/tasks/" + self.task11.key)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.url.endswith("/my"))

        project.message_partner_ids += portal_partner
        response = self.url_open("/tasks/" + self.task11.key)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"/my/tasks/{self.task11.id}", response.url)
