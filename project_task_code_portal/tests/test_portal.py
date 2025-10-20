# Copyright 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from lxml import html

from odoo import Command, tools
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.project.tests.test_access_rights import TestProjectPortalCommon


@tagged("-at_install", "post_install")
class TestPortalTaskCode(TestProjectPortalCommon, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super(TestPortalTaskCode, cls).setUpClass()
        cls.task_1.project_id.privacy_visibility = "portal"
        task_wizard = cls.env["portal.share"].create(
            {
                "res_model": "project.task",
                "res_id": cls.task_1.id,
                "partner_ids": [
                    Command.link(cls.partner_portal.id),
                ],
            }
        )
        task_wizard.action_send_mail()

        cls.host = "127.0.0.1"
        cls.port = tools.config["http_port"]
        cls.base_url = "http://%s:%d/my/tasks/" % (cls.host, cls.port)
        cls.url_task_code_pattern = "/my/tasks/{}?"

    def test_portal_tasks_list_access(self):
        self.authenticate("portal", "portal")
        response = self.url_open(self.base_url)
        content = response.content
        tree = html.fromstring(content)
        spans = tree.xpath(
            "//td[contains(@class, 'text-start') and contains(., '#')]//span"
        )
        list_tasks_code = [s.text for s in spans]
        self.assertIn(self.task_1.code, list_tasks_code)
        link = tree.xpath(f"//td[a/span[contains(text(), '{self.task_1.name}')]]//a")[
            0
        ].attrib["href"]
        self.assertEqual(link, self.url_task_code_pattern.format(self.task_1.code))

    def test_portal_task_access(self):
        self.authenticate("portal", "portal")
        response = self.url_open(self.base_url + self.task_1.code)
        content = response.content
        tree = html.fromstring(content)
        spans = tree.xpath(
            "//small[contains(@class, 'text-muted') and contains(@class, 'd-md-inline')]//span"
        )
        list_tasks_code = [s.text for s in spans]
        self.assertIn(self.task_1.code, list_tasks_code)

    def test_portal_task_not_found(self):
        self.authenticate("portal", "portal")
        response = self.url_open(self.base_url + "NoCode")
        home_url = "http://%s:%d/my" % (self.host, self.port)
        self.assertEqual(response.url, home_url)

    def test_portal_task_search_link_format(self):
        self.authenticate("portal", "portal")
        task_code = self.task_1.code
        query_params = f"?search_in=ref&search={task_code}"
        response = self.url_open(self.base_url[:-1] + query_params)
        content = response.content
        tree = html.fromstring(content)
        spans = tree.xpath(
            "//td[contains(@class, 'text-start') and contains(., '#')]//span"
        )
        list_tasks_code = [s.text for s in spans]
        self.assertIn(task_code, list_tasks_code)
        link = tree.xpath(f"//td[a/span[contains(text(), '{self.task_1.name}')]]//a")[
            0
        ].attrib["href"]
        self.assertEqual(
            link,
            self.url_task_code_pattern.format(self.task_1.code)[:-1] + query_params,
        )

    def test_portal_task_report(self):
        """Test task report generation through portal."""
        self.authenticate("portal", "portal")
        # Check if hr_timesheet module is installed
        hr_timesheet_installed = bool(
            self.env["ir.module.module"].search(
                [("name", "=", "hr_timesheet"), ("state", "=", "installed")]
            )
        )
        response = self.url_open(self.base_url + self.task_1.code + "?report_type=html")
        if hr_timesheet_installed:
            # If hr_timesheet is installed, expect successful response
            # _show_task_report is overridden by hr_timesheet to generate timesheet reports
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers.get("Content-Type", ""))
        else:
            # If hr_timesheet is not installed, expect error response
            # _show_task_report raises MissingError("There is nothing to report.")
            # This method is to be overriden to report timesheets if the module is installed
            self.assertEqual(response.status_code, 400)
            content = response.content
            tree = html.fromstring(content)
            error_elements = tree.xpath(
                "//pre[contains(text(), 'There is nothing to report.')]"
            )
            self.assertTrue(
                error_elements,
                "Error message 'There is nothing to report.' not found in response",
            )

    def test_portal_task_project_sharing(self):
        """Test project sharing functionality."""
        self.authenticate("portal", "portal")

        # First, access multiple tasks to build up history
        other_task = self.env["project.task"].create(
            {
                "name": "Other Task",
                "project_id": self.task_1.project_id.id,
            }
        )
        self.url_open(f"{self.base_url}{other_task.code}")

        # Share the project with portal user
        project_share_wizard = self.env["project.share.wizard"].create(
            {
                "access_mode": "edit",
                "res_model": "project.project",
                "res_id": self.task_1.project_id.id,
                "partner_ids": [Command.link(self.partner_portal.id)],
            }
        )
        project_share_wizard.action_send_mail()

        # Get the sharing link from the most recent mail message
        message = self.env["mail.message"].search(
            [
                ("partner_ids", "in", self.partner_portal.id),
                ("model", "=", "project.project"),
                ("res_id", "=", self.task_1.project_id.id),
            ],
            order="id DESC",
            limit=1,
        )

        share_link = str(message.body.split('href="')[1].split('">')[0])
        match = re.search(
            r"access_token=([^&]+)&amp;pid=([^&]+)&amp;hash=([^&]*)", share_link
        )
        access_token, pid, _hash = match.groups()

        # Access the task with project sharing context
        url = f"{self.base_url}{self.task_1.code}"

        # Get initial response to extract CSRF token
        initial_response = self.url_open(url)
        content = initial_response.text
        csrf_token = re.search(r'csrf_token: "([^"]+)"', content).group(1)

        # Make the POST request with CSRF token and project_sharing=True
        response = self.url_open(
            url=url,
            data={
                "csrf_token": csrf_token,
                "access_token": access_token,
                "project_sharing": True,
                "pid": pid,
                "hash": _hash,
            },
        )

        self.assertEqual(response.status_code, 200)

        # Now check if the navigation links for previous/next task are not present
        # This would indicate that the history was reset to only contain the current task
        content = response.content
        tree = html.fromstring(content)

        # Check for absence of navigation links (prev/next)
        # which would be present if history had multiple tasks
        prev_links = tree.xpath("//a[contains(@class, 'o_portal_pager_previous')]")
        next_links = tree.xpath("//a[contains(@class, 'o_portal_pager_next')]")

        # If history was reset to only current task, there should be no prev/next links
        self.assertFalse(
            prev_links, "Previous task link should not be present if history was reset"
        )
        self.assertFalse(
            next_links, "Next task link should not be present if history was reset"
        )


@tagged("-at_install", "post_install")
class TestPortalProjectTaskCode(TestProjectPortalCommon, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super(TestPortalProjectTaskCode, cls).setUpClass()
        cls.project_pigs.privacy_visibility = "portal"
        task_wizard = cls.env["portal.share"].create(
            {
                "res_model": "project.project",
                "res_id": cls.project_pigs.id,
                "partner_ids": [
                    Command.link(cls.partner_portal.id),
                ],
            }
        )
        task_wizard.action_send_mail()

        cls.host = "127.0.0.1"
        cls.port = tools.config["http_port"]
        cls.base_my_url = f"http://{cls.host}:{cls.port}/my"  # noqa: E231
        cls.base_projects_url = f"{cls.base_my_url}/projects"

        # Force activation because some modules might disable this rule
        cls.env.ref("project.project_task_rule_portal").write({"active": True})

    def test_portal_project_tasks_list_access(self):
        self.authenticate("portal", "portal")
        project_id = self.task_1.project_id.id
        url = f"{self.base_projects_url}/{project_id}"
        response = self.url_open(url)
        content = response.content
        tree = html.fromstring(content)
        spans = tree.xpath(
            "//td[contains(@class, 'text-start') and contains(., '#')]//span"
        )
        list_tasks_code = [s.text for s in spans]
        self.assertIn(self.task_1.code, list_tasks_code)
        link = tree.xpath(f"//td[a/span[contains(text(), '{self.task_1.name}')]]//a")[
            0
        ].attrib["href"]
        expected_link = f"/my/projects/{project_id}/task/{self.task_1.code}?"
        self.assertEqual(link, expected_link)

    def test_portal_my_project_task_ok(self):
        self.authenticate("portal", "portal")
        project_id = self.task_1.project_id.id
        task_code = self.task_1.code
        url = f"{self.base_projects_url}/{project_id}/task/{task_code}"
        response = self.url_open(url)
        content = response.content
        tree = html.fromstring(content)
        spans = tree.xpath(
            "//small[contains(@class, 'text-muted') and contains(@class, 'd-md-inline')]//span"
        )
        list_tasks_code = [s.text for s in spans]
        self.assertIn(self.task_1.code, list_tasks_code)

    def test_portal_my_project_task_not_found(self):
        self.authenticate("portal", "portal")
        project_id = self.task_1.project_id.id
        url = f"{self.base_projects_url}/{project_id}/task/NotExistentCode"
        response = self.url_open(url)
        self.assertEqual(response.url, self.base_my_url)

    def test_portal_my_project_task_no_access(self):
        other_project = self.env["project.project"].create(
            {
                "name": "Closed project",
                "privacy_visibility": "followers",
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Hidden task",
                "project_id": other_project.id,
                "code": "HIDDEN-CODE",
            }
        )
        self.authenticate("portal", "portal")
        url = f"{self.base_projects_url}/{other_project.id}/task/{task.code}"
        response = self.url_open(url)
        self.assertEqual(response.url, self.base_my_url)
