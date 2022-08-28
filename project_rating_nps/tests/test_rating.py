# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase

from .common import RatingTestMixin


class TestRating(RatingTestMixin, SavepointCase):

    def test_apply_rating_1(self):
        " Check rating_apply override works and uses present module images "

        self.task.rating_apply(self.rating.rating, self.rating.access_token,
                               feedback='test feedback')

        msg = self.task.message_ids.filtered(
            lambda m: 'test feedback' in m.body)

        rate = self.rating.rating
        self.assertIn('/project_rating_nps/static/src/img/rate_%d.png' % rate,
                      msg.body)

    def test_apply_rating_2(self):
        " Check task kanban state changes with the rating when configured to "

        self.assertEqual(self.task.kanban_state, "normal", "wrong rating initial state")
        self.task.stage_id.auto_validation_kanban_state = True

        self.task.rating_apply(6, self.rating.access_token)
        self.assertEqual(self.task.kanban_state, "blocked")

        self.task.rating_apply(9, self.rating.access_token)
        self.assertEqual(self.task.kanban_state, "done")
