# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from criticalpath import Node
except ImportError:
    _logger.debug('Cannot import `criticalpath`.')


class Project(models.Model):
    _inherit = 'project.project'

    @staticmethod
    def node_get_or_add(project_node, task_nodes, task):
        if task.id not in task_nodes.keys():
            node = project_node.add(Node(
                task.id,
                duration=task.critical_path_duration
            ))
            task_nodes.update({
                task.id: node
            })
        return task_nodes[task.id]

    @staticmethod
    def node_link(project_node, task_nodes, task):
        task_node = Project.node_get_or_add(project_node, task_nodes, task)
        for dep in task.dependency_task_ids:
            dep_node = Project.node_get_or_add(project_node, task_nodes, dep)
            project_node.link(dep_node, task_node)
            Project.node_link(project_node, task_nodes, dep)

    @api.model
    def calc_critical_path(self, project):
        task_nodes = {}
        project_node = Node('project')
        tasks = self.env['project.task'].search(
            [('project_id', '=', project.id)]
        )
        for task in tasks:
            Project.node_link(project_node, task_nodes, task)
        project_node.update_all()
        return [n.name for n in project_node.get_critical_path()]

    @api.model
    def calc_critical_paths(self, project_ids):
        res = {}
        projects = self.env['project.project'].browse(project_ids)
        for project in projects:
            res.update({
                project.id: self.calc_critical_path(project)
            })
        return res
