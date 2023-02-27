from odoo import fields, models, api


class ProjectTaskState(models.Model):
    _inherit = "project.task"

    pr_state = fields.Selection(
        selection=lambda self: self._selection_pr_state(),
        string="PR State",
        )

    @api.model
    def _selection_pr_state(self):
        """Function to select the state of the pull request"""
        return [
            ('open', 'Open'),
            ('draft', 'Draft'),
            ('merged', 'Merged'),
            ('closed', 'Closed'),
        ]

    @api.model
    def create(self, vals):
        new_rec = super(ProjectTaskState, self).create(vals)
        
        # Set pr state if URI is provided at creation
        if 'pr_uri' in vals:
            new_rec._set_pr_state(vals.get("pr_uri"))
        return new_rec

    def write(self, vals):
        if "pr_uri" in vals:
            self._set_pr_state(vals.get("pr_uri"), vals.get("pr_state"))
        return super(ProjectTaskState, self).write(vals)


    @api.onchange("pr_uri")
    def onchange_pr_uri(self):
        """Ser PR state when PR URI is entered in form"""
        if not self.pr_state and self.project_id and self.project_id.pr_state_default:
            self.pr_state = self.project_id.pr_state_default

    def _set_pr_state(self, pr_uri, pr_state=None):
        """Set PR state based on pr_uri
        This function is used to ensure correct state is set
        even if PR uri is changed from backend.

        Args:
            pr_uri (Char): PR URI
            pr_state (Selection): PR state
        """
        
        # Set state to False if PR URI is not set
        if not pr_uri:
            self.filtered("pr_state").write({"pr_state": False})

        # Set PR state explicitly
        elif pr_uri and pr_state is not None:
            self.filtered(lambda t: t.pr_state != pr_state).write({"pr_state": pr_state})
        
        # Set state for tasks based on Project default state
        else:
            projects = self.mapped("project_id").filtered(lambda p: p.pr_state_default)

            # Set value to all task at once to avoid extra db writes
            for project in projects:
                tasks = self.filtered(lambda t: t.project_id == project)
                tasks.write({"pr_state": project.pr_state_default})
                
        