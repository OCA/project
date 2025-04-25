from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.project.tests.test_project_base import TestProjectCommon


@tagged("-at_install", "post_install")
class TestProjectMerge(TestProjectCommon):
    def test_default_get_with_no_selected_tasks(self):
        """Test default_get behavior when no tasks are selected."""
        Wizard = self.env["project.task.merge"].with_context(active_ids=[])
        default_vals = Wizard.default_get(
            ["task_ids", "user_ids", "dst_project_id", "dst_task_id"]
        )
        self.assertFalse(default_vals.get("task_ids"), "Expected no tasks selected.")
        self.assertFalse(default_vals.get("user_ids"), "Expected no users assigned.")
        self.assertFalse(
            default_vals.get("dst_project_id"), "Expected no destination project."
        )
        self.assertFalse(
            default_vals.get("dst_task_id"), "Expected no destination task."
        )

    def test_merge_into_existing_task(self):
        """merging two tasks in to existing task"""
        task_A = self.env["project.task"].create(
            {
                "name": "Task A",
                "project_id": self.project_goats.id,
            }
        )
        child_1, child_2, child_3, child_4 = self.env["project.task"].create(
            [
                {
                    "name": "child 1",
                    "project_id": self.project_goats.id,
                    "parent_id": task_A.id,
                    "child_ids": [
                        Command.create(
                            {
                                "name": "Child 1 (Subtask 1)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Child 1 (Subtask 2)",
                                "project_id": self.project_goats.id,
                                "child_ids": [
                                    Command.create(
                                        {
                                            "name": "Subsubtask",
                                            "project_id": self.project_goats.id,
                                        }
                                    )
                                ],
                            }
                        ),
                    ],
                },
                {
                    "name": "child 2",
                    "project_id": self.project_goats.id,
                    "parent_id": task_A.id,
                },
                {
                    "name": "child 3",
                    "parent_id": task_A.id,
                    "project_id": self.project_goats.id,
                    "display_in_project": True,
                    "child_ids": [
                        Command.create(
                            {
                                "name": "Child 3 (Subtask 1)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Child 3 (Subtask 2)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                    ],
                },
                {
                    "name": "child 4",
                    "parent_id": task_A.id,
                    "project_id": self.project_goats.id,
                    "display_in_project": True,
                },
            ]
        )
        task_B = self.env["project.task"].create(
            {
                "name": "Task B",
                "project_id": self.project_goats.id,
            }
        )
        child_5, child_6, child_7, child_8 = self.env["project.task"].create(
            [
                {
                    "name": "child 5",
                    "project_id": self.project_goats.id,
                    "parent_id": task_B.id,
                    "child_ids": [
                        Command.create(
                            {
                                "name": "Child 5 (Subtask 1)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Child 5 (Subtask 2)",
                                "project_id": self.project_goats.id,
                                "child_ids": [
                                    Command.create(
                                        {
                                            "name": "Subsubtask",
                                            "project_id": self.project_goats.id,
                                        }
                                    )
                                ],
                            }
                        ),
                    ],
                },
                {
                    "name": "child 6",
                    "project_id": self.project_goats.id,
                    "parent_id": task_B.id,
                },
                {
                    "name": "child 7",
                    "parent_id": task_B.id,
                    "project_id": self.project_goats.id,
                    "display_in_project": True,
                    "child_ids": [
                        Command.create(
                            {
                                "name": "Child 7 (Subtask 1)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Child 7 (Subtask 2)",
                                "project_id": self.project_goats.id,
                            }
                        ),
                    ],
                },
                {
                    "name": "child 8",
                    "parent_id": task_B.id,
                    "project_id": self.project_goats.id,
                    "display_in_project": True,
                },
            ]
        )
        self.assertEqual(9, len(task_A._get_all_subtasks()), "A Should have A subtasks")

        self.task_merge_1 = (
            self.env["project.task.merge"]
            .with_context(active_ids=[task_A.id, task_B.id])
            .create({})
        )
        self.task_merge_1.merge_tasks()
        self.assertEqual(self.task_merge_1.dst_task_id.name, "Task A")
        self.assertEqual(child_5.parent_id.name, "Task A")
        self.assertEqual(child_8.parent_id.name, "Task A")
        self.assertEqual(child_1.parent_id.name, "Task A")
        self.assertEqual(
            18,
            len(self.task_merge_1.dst_task_id._get_all_subtasks()),
            "Should have 18 subtasks",
        )
        self.assertEqual(
            0, len(task_B._get_all_subtasks()), "Task Should have 0 subtasks"
        )

    def test_create_new_task_on_merge(self):
        """merging two tasks in to a new task"""
        task_A = self.env["project.task"].create(
            {
                "name": "Task A",
                "project_id": self.project_goats.id,
            }
        )
        (
            self.env["project.task"].create(
                [
                    {
                        "name": "child 1",
                        "project_id": self.project_goats.id,
                        "parent_id": task_A.id,
                        "child_ids": [
                            Command.create(
                                {
                                    "name": "Child 1 (Subtask 1)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                            Command.create(
                                {
                                    "name": "Child 1 (Subtask 2)",
                                    "project_id": self.project_goats.id,
                                    "child_ids": [
                                        Command.create(
                                            {
                                                "name": "Subsubtask",
                                                "project_id": self.project_goats.id,
                                            }
                                        )
                                    ],
                                }
                            ),
                        ],
                    },
                    {
                        "name": "child 2",
                        "project_id": self.project_goats.id,
                        "parent_id": task_A.id,
                    },
                    {
                        "name": "child 3",
                        "parent_id": task_A.id,
                        "project_id": self.project_goats.id,
                        "display_in_project": True,
                        "child_ids": [
                            Command.create(
                                {
                                    "name": "Child 3 (Subtask 1)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                            Command.create(
                                {
                                    "name": "Child 3 (Subtask 2)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                        ],
                    },
                    {
                        "name": "child 4",
                        "parent_id": task_A.id,
                        "project_id": self.project_goats.id,
                        "display_in_project": True,
                    },
                ]
            )
        )
        task_B = self.env["project.task"].create(
            {
                "name": "Task B",
                "project_id": self.project_goats.id,
            }
        )
        (
            self.env["project.task"].create(
                [
                    {
                        "name": "child 5",
                        "project_id": self.project_goats.id,
                        "parent_id": task_B.id,
                        "child_ids": [
                            Command.create(
                                {
                                    "name": "Child 5 (Subtask 1)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                            Command.create(
                                {
                                    "name": "Child 5 (Subtask 2)",
                                    "project_id": self.project_goats.id,
                                    "child_ids": [
                                        Command.create(
                                            {
                                                "name": "Subsubtask",
                                                "project_id": self.project_goats.id,
                                            }
                                        )
                                    ],
                                }
                            ),
                        ],
                    },
                    {
                        "name": "child 6",
                        "project_id": self.project_goats.id,
                        "parent_id": task_B.id,
                    },
                    {
                        "name": "child 7",
                        "parent_id": task_B.id,
                        "project_id": self.project_goats.id,
                        "display_in_project": True,
                        "child_ids": [
                            Command.create(
                                {
                                    "name": "Child 7 (Subtask 1)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                            Command.create(
                                {
                                    "name": "Child 7 (Subtask 2)",
                                    "project_id": self.project_goats.id,
                                }
                            ),
                        ],
                    },
                    {
                        "name": "child 8",
                        "parent_id": task_B.id,
                        "project_id": self.project_goats.id,
                        "display_in_project": True,
                    },
                ]
            )
        )
        self.task_merge_2 = (
            self.env["project.task.merge"]
            .with_context(active_ids=[task_A.id, task_B.id])
            .create({"create_new_task": True, "dst_task_name": "Test Merge Task"})
        )
        self.task_merge_2.merge_tasks()
        self.assertEqual(self.task_merge_2.dst_task_id.name, "Test Merge Task")
        self.assertEqual(
            18,
            len(self.task_merge_2.dst_task_id._get_all_subtasks()),
            "Should have 18 subtasks",
        )
