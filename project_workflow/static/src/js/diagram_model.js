// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
odoo.define('project_workflow.DiagramModel', function (require) {
"use strict";

require('web_diagram.DiagramModel').include({

    _fetchDiagramInfo: function () {
        if (!this.res_id) {
            return this.do_action({'type': 'history.back'});
        }
        return this._super.apply(this, arguments);
    },
});
});
