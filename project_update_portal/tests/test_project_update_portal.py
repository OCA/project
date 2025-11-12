# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import html

from odoo import tools
from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import users
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.project.tests.test_access_rights import TestProjectPortalCommon
from odoo.addons.project.tests.test_project_base import TestProjectCommon


@tagged("-at_install", "post_install")
class TestProjectUpdatePortal(TestProjectCommon):
    @classmethod
    def setUpClass(cls):
        super(TestProjectUpdatePortal, cls).setUpClass()
        # Create project updates
        cls.project_update_1 = cls.env["project.update"].create(
            {
                "name": "Test Project Update 1",
                "project_id": cls.project_pigs.id,
                "status": "on_track",
                "progress": 50,
            }
        )
        cls.project_update_2 = cls.env["project.update"].create(
            {
                "name": "Test Project Update 2",
                "project_id": cls.project_pigs.id,
                "status": "at_risk",
                "progress": 30,
            }
        )
        # Create another project with portal visibility
        cls.project_portal = (
            cls.env["project.project"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Portal Project",
                    "privacy_visibility": "portal",
                    "alias_name": "project+portal",
                    "partner_id": cls.partner_1.id,
                }
            )
        )
        cls.project_update_portal = cls.env["project.update"].create(
            {
                "name": "Portal Project Update",
                "project_id": cls.project_portal.id,
                "status": "on_track",
                "progress": 75,
            }
        )
        # Create portal user
        cls.portal_user = mail_new_test_user(
            cls.env, "Portal User", groups="base.group_portal"
        )
        # Create another portal user (not follower)
        cls.portal_user_no_access = mail_new_test_user(
            cls.env, "Portal User No Access", groups="base.group_portal"
        )

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_can_read_update_as_project_follower(self):
        """Portal user can read project update when following the project"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should be able to read the update
        update = self.project_update_1.with_user(self.env.user)
        update.invalidate_model()
        self.assertEqual(update.name, "Test Project Update 1")
        # Portal user should be able to search updates
        updates = (
            self.env["project.update"]
            .with_user(self.env.user)
            .search([("project_id", "=", self.project_pigs.id)])
        )
        self.assertIn(self.project_update_1, updates)
        self.assertIn(self.project_update_2, updates)

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_can_read_update_as_update_follower(self):
        """Portal user can read project update when following the update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to update (not project)
        self.project_update_1.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should be able to read the update
        update = self.project_update_1.with_user(self.env.user)
        update.invalidate_model()
        self.assertEqual(update.name, "Test Project Update 1")
        # Portal user should be able to search this specific update
        updates = (
            self.env["project.update"]
            .with_user(self.env.user)
            .search([("id", "=", self.project_update_1.id)])
        )
        self.assertIn(self.project_update_1, updates)

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_cannot_read_update_without_following(self):
        """Portal user cannot read project update when not following project or update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Portal user should not be able to read the update
        with self.assertRaises(
            AccessError,
            msg="Portal user should not be able to read update without following",
        ):
            self.project_update_1.with_user(self.env.user).name
        # Portal user should not be able to search updates (returns empty result set)
        updates = (
            self.env["project.update"]
            .with_user(self.env.user)
            .search([("project_id", "=", self.project_pigs.id)])
        )
        self.assertEqual(
            len(updates), 0, "Portal user should not see updates without following"
        )

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_cannot_read_update_when_project_not_portal(self):
        """Portal user cannot read project update when project is not portal visibility"""
        # Project is employees visibility by default
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should not be able to read the update
        with self.assertRaises(
            AccessError,
            msg="Portal user should not be able to read update when project is not portal",
        ):
            self.project_update_1.with_user(self.env.user).name

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_cannot_write_update(self):
        """Portal user cannot write project update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should not be able to write the update
        with self.assertRaises(
            AccessError, msg="Portal user should not be able to write update"
        ):
            self.project_update_1.with_user(self.env.user).write(
                {"name": "Modified Update"}
            )

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_cannot_create_update(self):
        """Portal user cannot create project update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should not be able to create update
        with self.assertRaises(
            AccessError, msg="Portal user should not be able to create update"
        ):
            self.env["project.update"].with_user(self.env.user).create(
                {
                    "name": "New Update",
                    "project_id": self.project_pigs.id,
                    "status": "on_track",
                }
            )

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_cannot_unlink_update(self):
        """Portal user cannot unlink project update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should not be able to unlink the update
        with self.assertRaises(
            AccessError, msg="Portal user should not be able to unlink update"
        ):
            self.project_update_1.with_user(self.env.user).unlink()

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_can_search_updates_as_project_follower(self):
        """Portal user can search project updates when following the project"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should be able to search updates
        updates = (
            self.env["project.update"]
            .with_user(self.env.user)
            .search([("project_id", "=", self.project_pigs.id)])
        )
        self.assertEqual(len(updates), 2)
        self.assertIn(self.project_update_1, updates)
        self.assertIn(self.project_update_2, updates)

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_can_read_multiple_updates(self):
        """Portal user can read multiple updates when following the project"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should be able to read both updates
        update1 = self.project_update_1.with_user(self.env.user)
        update2 = self.project_update_2.with_user(self.env.user)
        update1.invalidate_model()
        update2.invalidate_model()
        self.assertEqual(update1.name, "Test Project Update 1")
        self.assertEqual(update2.name, "Test Project Update 2")

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    @users("Portal User")
    def test_portal_user_can_read_update_fields(self):
        """Portal user can read all readable fields of project update"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Subscribe portal user to project
        self.project_pigs.with_user(self.user_projectmanager).message_subscribe(
            partner_ids=[self.portal_user.partner_id.id]
        )
        # Portal user should be able to read update fields
        update = self.project_update_1.with_user(self.env.user)
        update.invalidate_model()
        self.assertEqual(update.name, "Test Project Update 1")
        self.assertEqual(update.status, "on_track")
        self.assertEqual(update.progress, 50)
        self.assertEqual(update.project_id.id, self.project_pigs.id)

    @mute_logger("odoo.addons.base.models.ir_model", "odoo.addons.base.models.ir_rule")
    def test_portal_user_access_url(self):
        """Test that access_url is correctly computed for project updates"""
        # Set project to portal visibility
        self.project_pigs.privacy_visibility = "portal"
        # Compute access_url
        self.project_update_1._compute_access_url()
        expected_url = "/my/projects/%s/update/%s" % (
            self.project_pigs.id,
            self.project_update_1.id,
        )
        self.assertEqual(self.project_update_1.access_url, expected_url)


@tagged("-at_install", "post_install")
class TestProjectUpdatePortalRoutes(TestProjectPortalCommon, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super(TestProjectUpdatePortalRoutes, cls).setUpClass()
        cls.project_pigs.privacy_visibility = "portal"
        cls.project_update = cls.env["project.update"].create(
            {
                "name": "Portal Project Update",
                "project_id": cls.project_pigs.id,
                "status": "on_track",
                "progress": 60,
            }
        )

        # Ensure portal partner follows the project so that
        # project updates are visible by ir.rule
        cls.project_pigs.with_user(cls.user_projectmanager).message_subscribe(
            partner_ids=[cls.partner_portal.id]
        )

        cls.host = "127.0.0.1"
        cls.port = tools.config["http_port"]
        cls.base_my_url = f"http://{cls.host}:{cls.port}/my"  # noqa: E231
        cls.base_projects_url = f"{cls.base_my_url}/projects"

    def test_portal_project_updates_list_access(self):
        self.authenticate("portal", "portal")
        project_id = self.project_pigs.id
        url = f"{self.base_projects_url}/{project_id}/updates"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.content)
        links = tree.xpath(
            "//a[contains(@class, 'list-group-item')]["
            ".//h5[contains(text(), 'Portal Project Update')]]"
        )
        self.assertTrue(
            links,
            "Update link should be visible in project updates list",
        )
        href = links[0].attrib["href"]
        expected_href = f"/my/projects/{project_id}/update/{self.project_update.id}"
        self.assertEqual(href, expected_href)

    def test_portal_project_update_detail_access(self):
        self.authenticate("portal", "portal")
        project_id = self.project_pigs.id
        url = f"{self.base_projects_url}/{project_id}/update/{self.project_update.id}"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.content)
        headings = tree.xpath(
            "//h5[contains(@class, 'mb-0') and "
            "contains(normalize-space(.), 'Portal Project Update')]"
        )
        self.assertTrue(
            headings,
            "Update detail page should display the update title",
        )

    def test_portal_project_update_not_found(self):
        self.authenticate("portal", "portal")
        project_id = self.project_pigs.id
        url = f"{self.base_projects_url}/{project_id}/update/999999"
        response = self.url_open(url)
        expected_url = f"{self.base_projects_url}/{project_id}"
        self.assertEqual(response.url, expected_url)

    def test_portal_project_update_no_access(self):
        other_project = self.env["project.project"].create(
            {
                "name": "Closed project",
                "privacy_visibility": "followers",
            }
        )
        other_update = self.env["project.update"].create(
            {
                "name": "Hidden Project Update",
                "project_id": other_project.id,
                "status": "on_track",
                "progress": 10,
            }
        )
        self.authenticate("portal", "portal")
        url = (
            f"{self.base_projects_url}/{other_project.id}" f"/update/{other_update.id}"
        )
        response = self.url_open(url)
        self.assertEqual(response.url, self.base_my_url)
