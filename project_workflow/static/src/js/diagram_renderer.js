// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
odoo.define('project_workflow.DiagramRenderer', function (require) {
"use strict";

require('web_diagram.DiagramRenderer').include({

    _get_style: function(){
        var style = this._super();

        if (this.getParent().modelName === 'project.workflow') {
            style.yellow = "#f6c342";
            style.green = "#14892c";
            style.blue = "#4a6785";

            // Original node size:
            //style.node_size_x = 110; // width
            //style.node_size_y = 80;  // height

            style.node_size_x = 100;
            style.node_size_y = 30;
        }

        return style;
    },

});

});
