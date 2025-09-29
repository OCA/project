def post_init_hook(env):
    env.ref("project.project_task_rule_portal_project_sharing").write(
        {
            "domain_force": """
        [
            ('project_id.privacy_visibility', '=', 'portal'),
            ('active', '=', True),
            '|',
                ('project_id.message_partner_ids',
                 'child_of',
                 [user.partner_id.commercial_partner_id.id]),
                ('message_partner_ids',
                 'child_of',
                 [user.partner_id.commercial_partner_id.id]),
            ('project_id.edit_collaborator_ids.partner_id', 'in', [user.partner_id.id]),
        ]
        """
        }
    )
