# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Automating Project Task Scheduling",
    "version": "11.0.1.0.0",
    "category": "Project Management",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "depends": [
        "hr",
        "hr_timesheet",
        "project",
        "project_task_assignment",
        "project_task_dependency",
        "project_timeline",
        "project_stage_closed",
    ],
    "data": [
        "views/project_task_scheduling_menu_views.xml",
        "wizards/scheduling_wizard_views.xml",
        "views/project_task_scheduling_proposal_views.xml",
        "views/project_task_scheduling_views.xml",
    ],
    "installable": True,
}
