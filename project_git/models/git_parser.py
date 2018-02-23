# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import models, exceptions, _


class GitPayloadParser(models.AbstractModel):
    _name = 'project.git.payload.parser'

    def parse_header(self, context):
        parse_method_name = "parse_%s_header" % context.type

        if not hasattr(self, parse_method_name):
            raise exceptions.ValidationError(
                _("Unable to find header parsing method for '%s'") %
                context.type
            )

        return getattr(self, parse_method_name)(
            context.type, context.raw_payload
        )

    def parse(self, context):
        parse_method_name = "parse_%s_payload" % context.type

        if not hasattr(self, parse_method_name):
            raise exceptions.ValidationError(
                _("Unable to find parsing method for '%s'") % (context.type, )
            )

        return getattr(self, parse_method_name)(context)
