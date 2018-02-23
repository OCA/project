# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from lxml import etree
from odoo import models, tools


class XmlWorkflowWriter(models.AbstractModel):
    _inherit = 'project.workflow.xml.writer'

    def create_security_groups_element(self, parent, transition):
        """
        This method creates groups xml element.
        :param parent: The parent element of the new groups element.
        :param transition: The ``project.workflow`` browse object.
        :return: Returns a new groups xml element.
        """
        attributes = self.prepare_security_groups_attributes(transition)
        return etree.SubElement(parent, 'groups', attributes)

    def prepare_security_groups_attributes(self, transition):
        """
        This method prepares attribute values for a ``transitions`` element.
        At the moment this method does nothing but it's added here
        for possible future usage.
        :param transition: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {}

    def create_security_group_element(self, parent, group):
        """
        This method creates transition xml element.
        :param parent: The parent element of the new transition element.
        :param group: The ``project.workflow.transition`` browse object.
        :return: Returns a new transition xml element.
        """
        values = self.prepare_security_group_attributes(group)
        return etree.SubElement(parent, 'group', values)

    def prepare_security_group_attributes(self, group):
        """
        This method prepares attribute values for a transition element.
        :param group: The ``project.workflow.transition`` browse object.
        :return: Returns dictionary with attribute values.
        """
        values = {
            'name': group.name,
            'xml_id': self.get_group_xml_id(group.id)
        }

        return values

    @tools.ormcache('group_id')
    def get_group_xml_id(self, group_id):
        group_data = self.env['ir.model.data'].sudo().search([
            ('model', '=', 'res.groups'),
            ('res_id', '=', group_id)
        ])

        if group_data.exists():
            return "%s.%s" % (group_data.module, group_data.name)

        return 'NO_XML_ID'

    def create_transition_element(self, parent, transition):
        transition_element = super(XmlWorkflowWriter, self)\
            .create_transition_element(parent, transition)

        security_groups_element = self.create_security_groups_element(
            transition_element, transition
        )

        for group in transition.group_ids:
            self.create_security_group_element(security_groups_element, group)

        return transition_element
