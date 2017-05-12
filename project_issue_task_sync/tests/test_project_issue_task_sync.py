# -*- coding: utf-8 -*-
import openerp.tests.common as common


def fields_synced(task, issue):
    """
    check if fields are synced
    """
    return (
        task.stage_id == issue.stage_id and
        task.user_id == issue.user_id and
        task.description.replace('<p>', '').replace(
            '</p>', '') == issue.description.replace(
                '<p>', '').replace('</p>', '') and
        task.project_id == issue.project_id and
        task.name == issue.name
    )


class TestProjectIssuesTasksSync(common.TransactionCase):

    def setUp(self):
        super(TestProjectIssuesTasksSync, self).setUp()
        self.project_model = self.env['project.project']
        self.task_model = self.env['project.task']
        self.issue_model = self.env['project.issue']
        self.users_model = self.env['res.users']
        self.project1 = self.project_model.create({
            'name': 'PROJECT1_TEST',
            'use_issues': True,
            'use_tasks': True,
            'sync_tasks_issues': True
        })
        self.project2 = self.project_model.create({
            'name': 'PROJECT2_TEST',
            'use_issues': True,
            'use_tasks': True,
            'sync_tasks_issues': True
        })
        self.project_only_tasks = self.project_model.create({
            'name': 'PROJECT_ONLYTASKS',
            'use_issues': False,
            'use_tasks': True,
            'sync_tasks_issues': False
        })
        self.user_gio = self.users_model.create({
            'name': 'gio',
            'email': 'gio@gmail.com',
            'login': 'gio1',
            'alias_name': 'gio'
        })
        self.user_fefe = self.users_model.create({
            'name': 'fefe',
            'email': 'fefe@gmail.com',
            'login': 'fefe1',
            'alias_name': 'fefe'
        })

    def test_create_task(self):
        assertEqual = self.assertEqual
        new_task = self.task_model.create({
            'name': 'task1',
            'stage_id': '1',
            'user_id': self.user_gio.id,
            'description': 'task 1 to be synced',
            'project_id':  self.project1.id
        })
        # check if the create has worked
        assertEqual(len(new_task.issue_ids), 1)
        # check that they are actually in sync
        assertEqual(fields_synced(new_task, new_task.issue_ids[0]), True)
        binded_issues = new_task.issue_ids
        # Add 3 issues with a different user
        extra_issue_names = ['issue_a', 'issue_b', 'issue_c']
        extra_issues = []
        for name in extra_issue_names:
            ei = self.issue_model.create({
                'name': name,
                'user_id': self.user_fefe.id,
                'description': 'issue to be synced',
                'project_id':  self.project1.id,
                'task_id': new_task.id
            })
            extra_issues.append(ei)
        # add also the previous binded issue
        extra_issues.append(binded_issues)
        # verify extra_issues is 3+1=4 issues
        assertEqual(len(extra_issues), 4)
        new_task.write({
            'description': 'task_modified'
        })
        # now verify that task is updated with last issue write
        assertEqual(new_task.name, 'issue_c')
        # task should also be assigned to fefe
        assertEqual(new_task.user_id.id, self.user_fefe.id)
        # verify total sync of all extra issues and task 4.
        # they should. writing on new task triggered the sync of all connected
        # issues, the issues may not be updated between eachother.
        for curr_issue in extra_issues:
            assertEqual(fields_synced(new_task, curr_issue), True)
        # now delete task and check that all the issues are gone too.
        assertEqual(len(new_task.issue_ids), 4)
        connected_issues = new_task.issue_ids
        new_task.unlink()
        # verify that all connected issues to this task are deleted.
        for issue in connected_issues:
            assertEqual(
                self.issue_model.search([('id', '=', issue.id)]).ids, []
            )

    def test_create_issue(self):
        assertEqual = self.assertEqual
        new_issue = self.issue_model.create({
            'name': 'issue1',
            'user_id': self.user_fefe.id,
            'description': 'issue to be synced',
            'project_id': self.project1.id
        })
        # check if the create has worked and made us a new task.
        assertEqual(len(new_issue.task_id), 1)
        # check that they are actually in sync
        assertEqual(fields_synced(new_issue, new_issue.task_id), True)
        binded_task = new_issue.task_id
        new_issue.write({
            'description': 'is modified'
        })
        assertEqual(fields_synced(new_issue, binded_task), True)
        # change the binded task
        binded_task.write({'user_id': self.user_fefe.id})
        # now our issue should also be assigned to fefe
        assertEqual(new_issue.user_id.id, self.user_fefe.id)
        # verify total sync of this issue and it's task.
        assertEqual(
            fields_synced(new_issue, binded_task), True
        )
        # now delete task and check that all the issues are gone too.
        new_issue.unlink()
        # verify that the task binded to this issue was deleted
        assertEqual(
            self.task_model.search([('id', '=', binded_task.id)]).ids, []
        )

    def test_make_a_project_sync(self):
        # we take a unsynced project and give it 2 tasks
        assertEqual = self.assertEqual
        task_a = self.task_model.create({
            'name': 'taska',
            'stage_id': '1',
            'user_id': self.user_gio.id,
            'description': 'task 1 to be synced',
            'project_id':  self.project_only_tasks.id
        })

        task_b = self.task_model.create({
            'name': 'taskb',
            'stage_id': '1',
            'user_id': self.user_gio.id,
            'description': 'task 1 to be synced',
            'project_id': self.project_only_tasks.id
        })

        # verify
        assertEqual(
            set(self.task_model.search(
                [('project_id', '=', self.project_only_tasks.id)]
            ).ids),
            set([task_a.id, task_b.id])
        )
        assertEqual(
            self.issue_model.search(
                [('project_id', '=', self.project_only_tasks.id)]
            ).ids,
            []
        )
        # then we sync the project
        self.project_only_tasks.write({
            'use_issues': True,
            'use_tasks': True,
            'sync_tasks_issues': True
        })
        # so we should have 1 issue per task automatically generated/
        new_issues = self.issue_model.search(
            [('project_id', '=', self.project_only_tasks.id)]
        )
        assertEqual(len(new_issues), 0)
        # trigger the syncing post-creation
        self.project_only_tasks.sync_issues_for_tasks()
        new_issues = self.issue_model.search(
            [('project_id', '=', self.project_only_tasks.id)]
        )
        assertEqual(len(new_issues), 2)
        assertEqual(
            [x for x in new_issues.mapped(
                'task_id').ids if x not in [task_a.id, task_b.id]], []
        )
