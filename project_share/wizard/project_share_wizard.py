from odoo import Command, api, models


class ProjectShareWizard(models.TransientModel):
    _inherit = "project.share.wizard"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if result.get("collaborator_ids"):
            new_commands = []

            for cmd in result["collaborator_ids"]:
                # cmd is like (0, 0, values)
                if cmd[0] == 0:
                    values = dict(cmd[2])  # copy to not modify the original values

                    partner_id = values.get("partner_id")

                    # Search the original collaborator
                    collaborator = self.env["project.collaborator"].search(
                        [
                            ("partner_id", "=", partner_id),
                            ("project_id", "=", result.get("res_id")),
                        ],
                        limit=1,
                    )

                    # If not found, it is a follower with partner_share and
                    # readonly doesn't affect him
                    values["readonly"] = (
                        collaborator.readonly if collaborator else False
                    )

                    new_commands.append((0, 0, values))
                else:
                    new_commands.append(cmd)

            result["collaborator_ids"] = new_commands

        return result

    @api.model_create_multi
    def create(self, vals_list):
        wizards = super().create(vals_list)

        collaborator_ids_vals_list = []
        for wizard in wizards:
            project = wizard.resource_ref
            project_collaborator_per_partner_id = {
                c.partner_id.id: c for c in project.collaborator_ids
            }
            for collaborator in wizard.collaborator_ids:
                partner_id = collaborator.partner_id.id
                project_collaborator = project_collaborator_per_partner_id.get(
                    partner_id, self.env["project.collaborator"]
                )
                # readonly attribute only has sense if the access mode is not 'read',
                # otherwise kanban view won't be shown on portal
                readonly = collaborator.access_mode != "read" and collaborator.readonly
                collaborator_ids_vals_list.append(
                    Command.update(
                        project_collaborator.id,
                        {"readonly": readonly},
                    )
                )
        project_vals = {}
        if collaborator_ids_vals_list:
            project_vals["collaborator_ids"] = collaborator_ids_vals_list
        if project_vals:
            project.write(project_vals)

        return wizards
