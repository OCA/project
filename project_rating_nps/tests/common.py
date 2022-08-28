class RatingTestMixin:

    def setUp(self):
        super().setUp()

        env = self.env
        partner = env.ref("base.partner_demo")

        project = env['project.project'].create({
            'name': 'Test project',
            'rating_status': 'stage',
        })

        stage = self.env["project.task.type"].create({
            'name': 'Test stage',
            'project_ids': [(6, 0, project.ids)],
            })

        self.task = env['project.task'].create({
            'name': 'test task',
            'project_id': project.id,
            'stage_id': stage.id,
            'partner_id': partner.id,
        })

        self.rating = env["rating.rating"].create({
            'res_model_id': env['ir.model']._get('project.task').id,
            'res_id': self.task.id,
            'parent_res_model_id': env['ir.model']._get('project.project').id,
            'parent_res_id': project.id,
            'rated_partner_id': partner.id,
            'partner_id': partner.id,
            'rating': 8,
            'consumed': False,
        })
