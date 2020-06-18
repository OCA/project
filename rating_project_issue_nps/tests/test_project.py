from odoo.tests.common import at_install, post_install

from odoo.tests.common import TransactionCase


@at_install(False)
@post_install(True)
class ProjectTC(TransactionCase):

    def test_nps(self):
        project = self.env['project.project'].create({
            'name': u'Test project',
            'use_tasks': False,
            'use_issues': True,
            'rating_status': u'stage',
        })
        for num in range(11):
            issue = self.env['project.issue'].create({
                'project_id': project.id,
                'name': u'Issue %d' % num,
            })
        self.assertEqual(project.net_promoter_score, False)

        for num, issue in enumerate(project.issue_ids):
            token = issue.rating_get_access_token()
            rating = self.env['rating.rating'].search([
                ('access_token', '=', token),
            ])
            rating.write({'rating': num, 'consumed': True})
        self.assertEqual(project.net_promoter_score, int(100 * ((2-7) / 11.)))
