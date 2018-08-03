# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo.addons.project_task_scheduling.tests.common import \
    TestSchedulingCommon


class TestSchedulingProposal(TestSchedulingCommon):

    def test_action_recompute(self):
        self.wizard.action_accept()
        proposals = self.env['project.task.scheduling.proposal'].search([])
        best_proposal = proposals[-1]
        evaluation = best_proposal.evaluation
        new_proposal = best_proposal.copy()
        new_proposal.action_recompute()
        new_evaluation = new_proposal.evaluation
        self.assertEqual(evaluation, new_evaluation)

    def test_computed_fields(self):
        self.wizard.action_accept()
        proposals = self.env['project.task.scheduling.proposal'].search([])
        best_proposal = proposals[-1]
        date_end = best_proposal.date_end
        duration = best_proposal.duration
        delayed_tasks = best_proposal.delayed_tasks

        best_proposal._compute_end()
        best_proposal._compute_delayed_tasks()
        self.assertEqual(date_end, best_proposal.date_end)
        self.assertEqual(duration, best_proposal.duration)
        self.assertEqual(delayed_tasks, best_proposal.delayed_tasks)

    def test_action_set_scheduling(self):
        self.wizard.action_accept()
        proposals = self.env['project.task.scheduling.proposal'].search([])
        proposals[-1].action_timeline_scheduling()
        proposals[-1].action_set_scheduling()

        self.assertTrue(self.task_2.employee_id)
        self.assertTrue(self.task_2.date_start_assignation)
        self.assertTrue(self.task_2.date_stop_assignation)

        self.assertTrue(self.task_3.employee_id)
        self.assertTrue(self.task_3.date_start_assignation)
        self.assertTrue(self.task_3.date_stop_assignation)

        self.assertTrue(self.task_7.employee_id)
        self.assertTrue(self.task_7.date_start_assignation)
        self.assertTrue(self.task_7.date_stop_assignation)

        self.assertTrue(self.task_1.employee_id)
        self.assertTrue(self.task_1.date_start_assignation)
        self.assertTrue(self.task_1.date_stop_assignation)
