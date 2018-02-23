# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


def name(value):
    return {'name': value}


class XmlWorkflowReader(models.AbstractModel):
    _inherit = 'project.workflow.xml.reader'

    def read_transition(self, element):
        data = super(XmlWorkflowReader, self).read_transition(element)

        data['groups'] = self.read_security_groups(element)

        return data

    def read_security_groups(self, element):
        """
        Reads workflow security groups data out of the given xml element.
        :param element: The xml element which holds information
        about project workflow transitions.
        :return: Returns the workflow transitions.
        """
        groups = []
        for e in element.iterfind('groups/group'):
            groups.append(self.read_security_group(e))
        return groups

    def read_security_group(self, element):
        return {
            'name': self.read_string(element, 'name'),
            'xml_id': self.read_string(element, 'xml_id'),
        }

    def extend_rng(self, rng_etree):
        rng_etree = super(XmlWorkflowReader, self).extend_rng(rng_etree)
        root = rng_etree.getroot()

        root.insert(0, self.rng_define_groups())

        transition = root.xpath(
            "//rng:define[@name='transition']"
            "//rng:element[@name='transition']",
            namespaces=self._rng_namespace_map
        )[0]

        transition.append(self.rng_groups_element())
        return rng_etree

    def rng_define_groups(self):
        E = self.get_element_maker()

        doc = E.grammar(
            E.define(
                name('group'),
                E.element(
                    name('group'),
                    E.attribute(
                        name('name'),
                        E.text()
                    ),
                    E.attribute(
                        name('xml_id'),
                        E.text()
                    )
                )
            )
        )
        return doc[0]

    def rng_groups_element(self):
        E = self.get_element_maker()
        doc = E.grammar(
            E.optional(
                E.element(
                    name('groups'),
                    E.optional(
                        E.oneOrMore(
                            E.ref(
                                name("group")
                            )
                        )
                    )
                )
            )
        )
        return doc[0]
