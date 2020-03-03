# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Work Breakdown Structure - Tasks',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Matmoz d.o.o., '
              'Luxim d.o.o., '
              'Deneroteam, '
              'Eficent, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/project',
    'category': 'Project Management',
    'depends': ['project_wbs'],
    'data': [
        'view/project_task_view.xml',
        'view/project_view.xml',
    ],
    'installable': True,
}
