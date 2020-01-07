# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Wip',
    'summary': """Project Work in Progress metrics.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE INFORMÁTICA LTDA,Odoo Community Association (OCA)',
    'website': 'kmee.com.br',
    'depends': [
        'project',
        'project_stage_state',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_wip.xml',
        'views/project_task_view.xml',
        'views/project_project.xml',
        'views/report_project_value_stream.xml',
    ],
    'demo': [
    ],
}
