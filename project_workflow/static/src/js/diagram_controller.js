// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
odoo.define('project_workflow.DiagramController', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');
var rpc = require('web.rpc');

var _t = core._t;
var QWeb = core.qweb;

require('web_diagram.DiagramController').include({
    renderButtons: function ($node) {
        if (this.modelName === 'project.workflow') {
            var self = this;

            this.$buttons = $(QWeb.render("ProjectWorkflow.buttons", {'widget': this}));
            this.$buttons.on('click', '.o_diagram_edit', function() {
                self.edit_workflow();
            });

            this.$buttons.on('click', '.o_diagram_new_button', function() {
                self._addNode();
            });

            this.$buttons.on('click', '.o_diagram_publish', function() {
                self.button_workflow_publish();
            });

            this.$buttons.on('click', '.o_diagram_discard', function() {
                self.button_workflow_discard();
            });

            this.$buttons.on('click', '.o_diagram_export', function() {
                self.button_workflow_export();
            });

            $node = $node || this.options.$buttons;
            this.$buttons.appendTo($node);

        } else {
            this._super($node);
        }
    },

    _addNode(){
        return this._super.apply(this, arguments);
    },

    edit_workflow(){
        var self = this;
        rpc.query({
            model: 'ir.model.data',
            method: 'xmlid_to_res_id',
            args: ["project_workflow.edit_project_workflow"],
        }).then(function(view_id){
            var title = _t('Workflow');
            new dialogs.FormViewDialog(self, {
                res_model: self.modelName,
                res_id: self.model.res_id,
                view_id: view_id,
                context: self.context,
                title: _t("Edit:") + title,
                disable_multiple_selection: true,
            }).open();
        });
    },

    button_workflow_publish: function(){
        var self = this;
        var publish_workflow = function(){
            rpc.query({
                model: self.modelName,
                method: 'read',
                args: [[self.model.res_id], ['original_name']]
            }).then(function(data){
                var wkf_name = data[0].original_name;
                console.log(data);

                rpc.query({
                    model: 'project.workflow',
                    method: 'publish_workflow',
                    args: [self.model.res_id],
                    context: {diagram:true}
                }).then(function(result){
                    console.log("Publish Action: ", result);
                    if (result)
                        self.do_action(result);
                    else
                        return self.do_action({'type': 'history.back'}).then(function () {
                            Dialog.alert(self, _t("Workflow '" + wkf_name + "' has been successfully published!"));
                        });
                });
            });
        };

        Dialog.confirm(self, _t("Are you sure you want to publish this workflow?"), { confirm_callback: publish_workflow })
    },

    button_workflow_discard: function(){
        var self = this;

        var discard_workflow = function(){
            rpc.query({
                model: 'project.workflow',
                method: 'discard_working_copy',
                args: [[self.model.res_id]],
            }).then(function(result){
                if (result)
                    self.do_action(result);
            });
        }

        Dialog.confirm(self, _t("Are you sure you want to discard this workflow?"), { confirm_callback: discard_workflow })
    },

    button_workflow_export: function () {
        var self = this;

        rpc.query({
            model: 'project.workflow',
            method: 'export_workflow',
            args: [self.model.res_id],
        }).then(function(result) {
            self.do_action(result);
        });
    },
});

});
