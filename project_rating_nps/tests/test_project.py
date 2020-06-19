# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProjectRatingNPS(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectRatingNPS, cls).setUpClass()
        cls.project = cls.env['project.project'].create({
            'name': u'Test project',
            'rating_status': u'stage',
        })

    def test_nps(self):
        for num in range(11):
            task = self.env['project.task'].create({
                'project_id': self.project.id,
                'name': u'Issue Task %d' % num,
            })
        self.assertEqual(self.project.net_promoter_score, False)

        for num, task in enumerate(self.project.task_ids):
            token = task.rating_get_access_token()
            rating = self.env['rating.rating'].search([
                ('access_token', '=', token),
            ])
            rating.write({'rating': num, 'consumed': True})
        self.assertEqual(self.project.net_promoter_score, int(100 * ((2-7) / 11.)))
