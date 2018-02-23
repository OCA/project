# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import os
import logging

from lxml import etree
from lxml.builder import ElementMaker

from odoo import models, tools, exceptions, _

_logger = logging.getLogger(__name__)


class XmlWorkflowReader(models.AbstractModel):
    _name = 'project.workflow.xml.reader'

    _rng_namespace = 'http://relaxng.org/ns/structure/1.0'
    _rng_namespace_map = {'rng': 'http://relaxng.org/ns/structure/1.0'}

    def get_element_maker(self):
        return ElementMaker(
            namespace=self._rng_namespace,
            nsmap=self._rng_namespace_map,
        )

    def validate_schema(self, xml):
        """
        Validates given ``xml`` against RelaxedNG validation schema.
        In case xml is invalid and ~openerp.exceptions.ValidationError
        is raised.
        :param xml: Xml string to be validated against RelaxedNG schema
        :return: Void
        """
        validator = self.create_validator()
        if not validator.validate(xml):
            errors = []
            for error in validator.error_log:
                error = tools.ustr(error)
                _logger.error(error)
                errors.append(error)
            raise exceptions.ValidationError(
                _("Workflow File Validation Error: %s" % ",".join(errors))
            )

    def create_validator(self):
        """
        Instantiates RelaxedNG schema validator
        :return: Returns RelaxedNG validator
        """
        rng_file = tools.file_open(self.get_rng_file_path())
        try:
            rng = etree.parse(rng_file)
            rng = self.extend_rng(rng)
            return etree.RelaxNG(rng)
        except Exception:
            raise
        finally:
            rng_file.close()

    def extend_rng(self, rng_etree):
        """
        This method is a hook from where you can modify rng schema in cases
        where you have extend workflow from another module and you want to
        support import/export functionality for your extensions.
        :param rng_etree: The tng tree which needs to be extended.
        :return: Returns extended rng tree.
        """
        return rng_etree

    def get_rng_file_path(self):
        return os.path.join('project_workflow', 'rng', 'workflow.rng')

    def wkf_read(self, stream):
        """
        Reads workflow from the given xml string
        :param stream: The stream providing xml data
        :return: Returns parsed workflow data.
        """

        workflow_tree = etree.parse(stream)
        self.validate_schema(workflow_tree)

        workflow_xml = workflow_tree.getroot()

        workflow = self.read_workflow(workflow_xml)
        self.validate_workflow(workflow)

        return workflow

    def validate_workflow(self, workflow):
        """
        This method validates the logic of the given workflow object.
        It will check if all source and destinations states referenced
        in the transition element can be found within defined workflow
        states.
        :param workflow: The
        :return:
        """

        # Convert list of workflow states into dictionary
        states = dict((s['name'], s) for s in workflow['states'])

        # If the count of states in list and dictionary is different
        # then we have a potential problem
        if len(states) != len(workflow['states']):
            raise exceptions.ValidationError(
                _("You have defined one or more states with the same name!")
            )

        # Next we check if all source and destination states can be found
        # in the states dictionary
        missing_states = set()
        for transition in workflow['transitions']:
            for state in ['src', 'dst']:
                value = transition[state]
                if value not in states:
                    missing_states.add(value)

        # In case we have missing states we simply raise exception
        if len(missing_states) > 0:
            raise exceptions.ValidationError(_(
                "Following state(s) are referenced in the transitions but can"
                " not be found: [%s]"
            ) % ",".join(missing_states))

        if not workflow.get('default_state', False):
            raise exceptions.ValidationError(
                _("Workflow default state is missing!")
            )

    def read_workflow(self, element):
        """
        Reads workflow data out of the given xml element.
        :param element: The xml element which holds information
        about project workflow.
        :return: Returns workflow dictionary.
        """
        return {
            'name': self.read_string(element, 'name'),
            'description': self.read_string(element, 'description'),
            'states': self.read_states(element),
            'transitions': self.read_transitions(element),
            'default_state': self.read_string(element, 'default-state')
        }

    def read_states(self, element):
        """
        Reads workflow states data out of the given xml element.
        :param element: The xml element which holds information
        about project workflow states
        :return: Returns the list of the workflow states
        """
        states = []
        for e in element.iterfind('states/state'):
            states.append(self.read_state(e))
        return states

    def read_state(self, element):
        """
        Reads workflow state data out of the given xml element.
        :param element: The xml element which holds information
        about project workflow state
        :return: Returns workflow state dictionary
        """
        return {
            'name': self.read_string(element, 'name'),
            'type': self.read_string(element, 'type', 'in_progress'),
            'description': self.read_string(element, 'description'),
            'xpos': self.read_integer(element, 'xpos', -1),
            'ypos': self.read_integer(element, 'ypos', -1),
            'sequence': self.read_integer(
                element, 'sequence', default_value=1),
            'kanban_sequence': self.read_integer(
                element, 'kanban_sequence', default_value=10)
        }

    def read_transitions(self, element):
        """
        Reads workflow transitions data out of the given xml element.
        :param element: The xml element which holds information about
        project workflow transitions.
        :return: Returns the list of the workflow transitions.
        """
        transitions = []
        for e in element.iterfind('transitions/transition'):
            transitions.append(self.read_transition(e))
        return transitions

    def read_transition(self, element):
        """
        Reads ``project.workflow.transition`` data
        out of the given xml element.
        :param element: The xml element which holds information
        about project workflow transition.
        :return: Returns workflow transition dictionary.
        """
        return {
            'name': self.read_string(element, 'name'),
            'description': self.read_string(element, 'description'),
            'src': self.read_string(element, 'src'),
            'dst': self.read_string(element, 'dst'),
            'confirmation': self.read_string(element, 'confirmation'),
            'kanban_color': self.read_string(
                element, 'kanban-color', default_value='1')
        }

    def read_string(self, element, attribute_name, default_value=''):
        """
        Reads attribute of type ``string`` from the given xml element.
        :param element: The xml element from which the attribute value is read.
        :param attribute_name: The name of the xml attribute.
        :param default_value: The default value in case
        the attribute is not present within xml element.
        :return: Returns attribute value of type ``string``
        """
        return self.read_attribute(element, attribute_name, default_value)

    def read_integer(self, element, attribute_name, default_value=0):
        """
        Reads attribute of type ``integer`` from the given xml element.
        :param element: The xml element from which the attribute value is read.
        :param attribute_name: The name of the xml attribute.
        :param default_value: The default value in case
        the attribute is not present within xml element.
        :return: Returns attribute value of type ``integer``.
        """
        return int(self.read_attribute(element, attribute_name, default_value))

    def read_boolean(self, element, attribute_name, default_value=False):
        """
        Reads attribute of type ``boolean`` from the given xml element.
        :param element: The xml element from which the attribute value is read.
        :param attribute_name: The name of the xml attribute.
        :param default_value: The default value in case
        the attribute is not present within xml element.
        :return: Returns attribute value of type ``boolean``.
        """
        return bool(self.read_attribute(
            element, attribute_name, default_value)
        )

    def read_attribute(self, element, name, default_value=None):
        """
        Reads attribute value of the given ``name`` from the given xml element.
        :param element: The xml element from which attribute.
        :param name: The name of the attribute.
        :param default_value: The default value in case
        the attribute is not present within xml element.
        :return: Returns attribute value or the default value.
        """
        return element.attrib.get(name, default_value)


DEFAULT_ENCODING = 'utf-8'


class XmlWorkflowWriter(models.AbstractModel):
    _name = 'project.workflow.xml.writer'

    def wkf_write(self, workflow, stream, encoding=DEFAULT_ENCODING):
        """
        Converts given ``workflow`` object to the xml and then
        writes it down to the given ``stream`` object.
        :param workflow: The ``project.workflow`` browse object
        to be written down to the given stream object.
        :param stream: This object represent any data stream object
         but it must have write method.
        :return:
        """
        str = self.to_string(workflow, encoding)
        if encoding != "unicode":
            str = str.decode(encoding)
        stream.write(str)

    def to_string(self, workflow, encoding=DEFAULT_ENCODING):
        """
        Gets xml string representation of the given ``workflow`` object.
        :param workflow: The ``project.workflow`` browse object
        to be converted to the xml string.
        :return: Returns xml string representation
        of the give ``workflow`` object.
        """
        return etree.tostring(
            self._build_xml(workflow, element_tree=True),
            encoding=encoding,
            pretty_print=True
        )

    def _build_xml(self, workflow, element_tree=False):
        """
        Builds xml out of given ``workflow`` object.
        :param workflow: The ``project.workflow`` browse object.
        :param element_tree: Boolean indicating whteter to wrap
        root element into ``ElementTree`` or not.
        :return: Returns workflow xml as a root element or as an element tree.
        """
        root = self.create_workflow_element(workflow)

        states = self.create_states_element(root, workflow)
        for state in workflow.state_ids:
            self.create_state_element(states, state)

        transitions = self.create_transitions_element(root, workflow)
        for transition in workflow.transition_ids:
            self.create_transition_element(transitions, transition)

        return element_tree and etree.ElementTree(root) or root

    def create_workflow_element(self, workflow):
        """
        This method creates root workflow xml element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new root workflow xml element.
        """
        attributes = self.prepare_workflow_attributes(workflow)
        return etree.Element('project-workflow', attributes)

    def prepare_workflow_attributes(self, workflow):
        """
        This method prepares attribute values for a workflow element.
        :param state: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {
            'name': workflow.name,
            'description': workflow.description,
            'default-state': workflow.default_state_id.name
        }

    def create_states_element(self, parent, workflow):
        """
        This method creates state xml element.
        :param parent: The parent element of the new states element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new state xml element.
        """
        attributes = self.prepare_states_attributes(workflow)
        return etree.SubElement(parent, 'states', attributes)

    def prepare_states_attributes(self, workflow):
        """
        This method prepares attribute values for a ``states`` element.
        At the moment this method does nothing but it's added here
        for possible future usage.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {}

    def create_state_element(self, parent, state):
        """
        This method creates state xml element.
        :param parent: The parent element of the new state element.
        :param state: The ``project.workflow.state`` browse object.
        :return: Returns a new state xml element.
        """
        attributes = self.prepare_state_attributes(state)
        return etree.SubElement(parent, 'state', attributes)

    def prepare_state_attributes(self, state):
        """
        This method prepares attribute values for a state element.
        :param state: The ``project.workflow.state`` browse object.
        :return: Returns dictionary with attribute values.
        """
        values = {
            'name': state.stage_id.name,
            'type': state.type,
            'xpos': str(state.xpos),
            'ypos': str(state.ypos),
            'sequence': str(state.sequence),
            'kanban_sequence': str(state.kanban_sequence),
        }

        if state.stage_id.description:
            values['description'] = state.description

        return values

    def create_transitions_element(self, parent, workflow):
        """
        This method creates transition xml element.
        :param parent: The parent element of the new transition element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new transition xml element.
        """
        attributes = self.prepare_transitions_attributes(workflow)
        return etree.SubElement(parent, 'transitions', attributes)

    def prepare_transitions_attributes(self, workflow):
        """
        This method prepares attribute values for a ``transitions`` element.
        At the moment this method does nothing but it's added here
        for possible future usage.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {}

    def create_transition_element(self, parent, transition):
        """
        This method creates transition xml element.
        :param parent: The parent element of the new transition element.
        :param transition: The ``project.workflow.transition`` browse object.
        :return: Returns a new transition xml element.
        """
        values = self.prepare_transition_attributes(transition)
        return etree.SubElement(parent, 'transition', values)

    def prepare_transition_attributes(self, transition):
        """
        This method prepares attribute values for a transition element.
        :param transition: The ``project.workflow.transition`` browse object.
        :return: Returns dictionary with attribute values.
        """
        values = {
            'name': transition.name,
            'src': transition.src_id.stage_id.name,
            'dst': transition.dst_id.stage_id.name,
            'confirmation': str(transition.user_confirmation or False),
        }

        if transition.description:
            values['description'] = transition.description

        return values
