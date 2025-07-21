# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tests import common as tests_common

from odoo.addons.base.tests.common import BaseCommon


@tests_common.tagged("-at_install", "post_install")
class TestStageChangeRestriction(BaseCommon):
    """Validate stage-change & creation access rules for project tasks."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env

        gp_user = env.ref("project.group_project_user")
        gp_manager = env.ref("project.group_project_manager")
        try:
            cls.grp_sales_admin = env.ref("sale.group_sale_manager")
        except ValueError:
            cls.grp_sales_admin = env["res.groups"].create(
                {"name": "Sales / Manager (Test)"}
            )

        def _mk_user(login, groups):
            return (
                env["res.users"]
                .with_user(SUPERUSER_ID)
                .create(
                    {
                        "name": login.replace("_", " ").title(),
                        "login": login,
                        "groups_id": [(4, g.id) for g in groups],
                    }
                )
            )

        cls.user_dev = _mk_user("dev_user", [gp_user])
        cls.user_pm = _mk_user("pm_user", [gp_user, gp_manager])
        cls.user_sales = _mk_user("sales_user", [gp_user, cls.grp_sales_admin])

        cls.project = (
            env["project.project"]
            .with_user(SUPERUSER_ID)
            .create(
                {
                    "name": "Demo Project",
                    "user_id": cls.user_pm.id,
                }
            )
        )

        Stage = env["project.task.type"].with_user(SUPERUSER_ID).create
        cls.stage_free = Stage({"name": "Free"})
        cls.stage_assigned = Stage(
            {"name": "Assigned Only", "allow_assigned_only": True}
        )
        cls.stage_pm = Stage(
            {"name": "Project Manager Only", "allow_project_manager": True}
        )
        cls.stage_group = Stage(
            {
                "name": "Sales Only",
                "allow_group_ids": [(6, 0, [cls.grp_sales_admin.id])],
            }
        )
        cls.stage_assigned_or_pm = Stage(
            {
                "name": "Assigned OR PM",
                "allow_assigned_only": True,
                "allow_project_manager": True,
            }
        )
        cls.stage_assigned_or_group = Stage(
            {
                "name": "Assigned OR Sales",
                "allow_assigned_only": True,
                "allow_group_ids": [(6, 0, [cls.grp_sales_admin.id])],
            }
        )
        cls.stage_pm_or_group = Stage(
            {
                "name": "PM OR Sales",
                "allow_project_manager": True,
                "allow_group_ids": [(6, 0, [cls.grp_sales_admin.id])],
            }
        )

        cls.task_tpl = (
            env["project.task"]
            .with_user(SUPERUSER_ID)
            .create(
                {
                    "name": "Template Task",
                    "project_id": cls.project.id,
                    "stage_id": cls.stage_free.id,
                }
            )
        )

    def _clone_task(self, acting_user, *, assignees=None, stage=None):
        """Copy template and return it **as** ``acting_user``.

        :param acting_user: user performing follow‑up actions
        :param assignees: list/tuple of users assigned to the task
        :param stage: optional initial stage
        """
        vals = {
            "user_ids": [(6, 0, [u.id for u in (assignees or [])])],
            "project_id": self.project.id,
        }
        if stage:
            vals["stage_id"] = stage.id
        return self.task_tpl.copy(vals).with_user(acting_user)

    def _ok_move(self, task, user, stage):
        """
        Assert that `user` is allowed to move `task` to `stage`.

        :raises AssertionError: if the stage was not applied
        """
        task.with_user(user).write({"stage_id": stage.id})
        self.assertEqual(task.stage_id, stage)

    def _fail_move(self, task, user, stage):
        """
        Assert that `user` is NOT allowed to move `task` to `stage`.

        :raises UserError: if the write does not fail as expected
        """
        with self.assertRaises(UserError):
            task.with_user(user).write({"stage_id": stage.id})

    def _ok_create(self, creator, stage, *, assignees=None):
        """
        Assert that `creator` may create a task in `stage` (with optional assignees).

        :returns: the newly created task record
        :raises AssertionError: if the task is not in the expected stage
        """
        rec = (
            self.env["project.task"]
            .with_user(creator)
            .create(
                {
                    "name": "Task",
                    "project_id": self.project.id,
                    "stage_id": stage.id,
                    "user_ids": [(6, 0, [u.id for u in (assignees or [])])],
                }
            )
        )
        self.assertEqual(rec.stage_id, stage)

    def _fail_create(self, creator, stage, *, assignees=None):
        """
        Assert that `creator` may NOT create a task in `stage`.

        :raises UserError: if the create does not fail as expected
        """
        with self.assertRaises(UserError):
            self.env["project.task"].with_user(creator).create(
                {
                    "name": "Bad",
                    "project_id": self.project.id,
                    "stage_id": stage.id,
                    "user_ids": [(6, 0, [u.id for u in (assignees or [])])],
                }
            )

    def test_move_free(self):
        task = self._clone_task(self.user_dev)
        for u in (self.user_dev, self.user_pm, self.user_sales):
            self._ok_move(task, u, self.stage_free)

    def test_move_assigned_only(self):
        task = self._clone_task(self.user_dev, assignees=[self.user_dev])
        self._ok_move(task, self.user_dev, self.stage_assigned)
        self._fail_move(task, self.user_pm, self.stage_assigned)
        self._fail_move(task, self.user_sales, self.stage_assigned)

    def test_move_pm_only(self):
        task = self._clone_task(self.user_dev)
        self._ok_move(task, self.user_pm, self.stage_pm)
        self._fail_move(task, self.user_dev, self.stage_pm)
        self._fail_move(task, self.user_sales, self.stage_pm)

    def test_move_group_only(self):
        task = self._clone_task(self.user_dev)
        self._ok_move(task, self.user_sales, self.stage_group)
        self._fail_move(task, self.user_dev, self.stage_group)
        self._fail_move(task, self.user_pm, self.stage_group)

    def test_move_assigned_or_pm(self):
        task = self._clone_task(self.user_dev, assignees=[self.user_dev])
        self._ok_move(task, self.user_dev, self.stage_assigned_or_pm)
        self._ok_move(task, self.user_pm, self.stage_assigned_or_pm)
        self._fail_move(task, self.user_sales, self.stage_assigned_or_pm)

    def test_move_assigned_or_group(self):
        task = self._clone_task(self.user_dev, assignees=[self.user_dev])
        self._ok_move(task, self.user_dev, self.stage_assigned_or_group)
        self._ok_move(task, self.user_sales, self.stage_assigned_or_group)
        self._fail_move(task, self.user_pm, self.stage_assigned_or_group)

    def test_move_pm_or_group(self):
        task = self._clone_task(self.user_dev)
        self._ok_move(task, self.user_pm, self.stage_pm_or_group)
        self._ok_move(task, self.user_sales, self.stage_pm_or_group)
        self._fail_move(task, self.user_dev, self.stage_pm_or_group)

    def test_superuser_bypass_move(self):
        task = self._clone_task(self.user_dev)
        task.with_user(SUPERUSER_ID).write({"stage_id": self.stage_pm.id})
        self.assertEqual(task.stage_id, self.stage_pm)

    def test_create_free(self):
        for u in (self.user_dev, self.user_pm, self.user_sales):
            self._ok_create(u, self.stage_free)

    def test_create_assigned_only(self):
        self._ok_create(self.user_dev, self.stage_assigned, assignees=[self.user_dev])
        self._fail_create(self.user_pm, self.stage_assigned, assignees=[self.user_dev])
        self._fail_create(
            self.user_sales, self.stage_assigned, assignees=[self.user_dev]
        )

    def test_create_pm_only(self):
        self._ok_create(self.user_pm, self.stage_pm)
        self._fail_create(self.user_dev, self.stage_pm)
        self._fail_create(self.user_sales, self.stage_pm)

    def test_create_group_only(self):
        self._ok_create(self.user_sales, self.stage_group)
        self._fail_create(self.user_dev, self.stage_group)
        self._fail_create(self.user_pm, self.stage_group)

    def test_create_assigned_or_pm(self):
        self._ok_create(
            self.user_dev, self.stage_assigned_or_pm, assignees=[self.user_dev]
        )
        self._ok_create(self.user_pm, self.stage_assigned_or_pm)
        self._fail_create(
            self.user_sales, self.stage_assigned_or_pm, assignees=[self.user_dev]
        )

    def test_create_assigned_or_group(self):
        self._ok_create(
            self.user_dev, self.stage_assigned_or_group, assignees=[self.user_dev]
        )
        self._ok_create(self.user_sales, self.stage_assigned_or_group)
        self._fail_create(
            self.user_pm, self.stage_assigned_or_group, assignees=[self.user_dev]
        )

    def test_create_pm_or_group(self):
        self._ok_create(self.user_pm, self.stage_pm_or_group)
        self._ok_create(self.user_sales, self.stage_pm_or_group)
        self._fail_create(self.user_dev, self.stage_pm_or_group)

    def test_superuser_bypass_create(self):
        rec = (
            self.env["project.task"]
            .with_user(SUPERUSER_ID)
            .create(
                {
                    "name": "SU task",
                    "project_id": self.project.id,
                    "stage_id": self.stage_assigned.id,
                }
            )
        )
        self.assertEqual(rec.stage_id, self.stage_assigned)
