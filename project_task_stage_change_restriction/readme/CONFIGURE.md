The **Task Stages** menu is only visible when Odoo is in developer mode.
Please turn on developer mode before proceeding.

Go to "Project > Configuration > Task Stages" and select or create a new task stage.
Configure the following fields in the "Stage Change Restriction" group:

- **Assigned Only**  
  If enabled, only users assigned to the task can move it into this stage.
- **Project Manager**  
  If enabled, only the manager of the project this task belongs to can move it.
- **Group Members**  
  Select groups whose members can move tasks into this stage.

Please be advised, that selected conditions are evaluated using the "OR" principle. So, a user should satisfy any of the selected conditions.

NB: restrictions are not applied if a stage is being changed by a superuser.
