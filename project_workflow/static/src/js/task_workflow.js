// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

odoo.define('project_workflow.TaskWorkflow', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var field_registry = require('web.field_registry');


    var AbstractField = require('web.AbstractField');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var DEFAULT_VISIBLE_TRANSITIONS = 3;

    var TaskWorkflow = AbstractField.extend({
        className: 'o_statusbar_status',
        events: {
            'click button:not(.dropdown-toggle)': '_onClickStage',
        },
        supportedFieldTypes: ['many2one'],

        init: function () {
            this._super.apply(this, arguments);
            this._onClickStage = _.debounce(this._onClickStage, 300, true); // TODO maybe not useful anymore ?

            this.nodeOptions.no_visible_transitions = this.nodeOptions.no_visible_transitions || DEFAULT_VISIBLE_TRANSITIONS;
            this.max_visible_transitions = this.nodeOptions.no_visible_transitions;

            this.confirmation_action = {
                module:"project_workflow",
                xml_id:"wkf_project_task_confirmation_action",
            };
        },

        willStart: function(){
            var self = this;
            return this._super.apply(this, arguments).then(()=> {
                return self._fetch_available_transitions();
            });
        },

        _fetch_available_transitions: function () {
            let self = this;
            return rpc.query({
                model: 'project.workflow',
                method: 'get_state_transitions',
                args: [this.recordData.workflow_id.res_id, this.recordData.stage_id.res_id, this.recordData.id],
            }).then(function (transitions) {

                self.transitions_available = {};

                _.each(transitions, function (transition) {
                    self.transitions_available[transition.id] = transition;
                });

                let count = 0

                transitions = transitions.sort((a, b) => a.sequence > b.sequence);

                self.transitions_visible = [];
                while(count < transitions.length && count < self.max_visible_transitions){
                    self.transitions_visible.push(transitions[count++]);
                }

                self.transitions_hidden = [];
                while (count < transitions.length){
                    self.transitions_hidden.push(transitions[count++]);
                }
            });
        },

        _render: function() {
            this.$el.off('click','button[data-id]',this._onClickStage);

            var $content = $(QWeb.render("TaskWorkflowNavigation.content", {
                'widget': this,
            }));

            this.$el.empty().append($content.get().reverse());
            this.$el.on('click','button[data-id]',this._onClickStage);
        },

        _onClickStage: function (e) {
            let state = this.transitions_available[$(e.currentTarget).data("value")]

            if (state.confirmation){
                this._do_confirmation(state);
            } else {
                this._update_state(state);
            }
        },

        _update_state: function(state){
            this.getParent().trigger_up('field_changed', {
                dataPointID: this.getParent().state.id,
                changes: this._prepare_values_for_update(state),
            });
        },

        _prepare_values_for_update(state){
            let changes = {};
            changes['stage_id'] = { id: state.id };
            return changes;
        },

        _do_confirmation: function(state){
            var self = this;
            return rpc.query({
                    model: 'ir.actions.act_window',
                    method: 'for_xml_id',
                    args: [this.confirmation_action.module, this.confirmation_action.xml_id],
                }).then(function(action){
                    var options = self.build_confirmation_options(state);
                    return self.do_action(action, options);
                });
        },

        build_confirmation_context: function(state){
            let parent = this.getParent();
            let parent_state = parent.state;
            var context = parent_state.getContext();
            context['default_task_id'] = this.res_id;
            context['default_stage_id'] = state.id;
            return context;
        },

        build_confirmation_options: function (state) {
            var self = this;
            var options = {};
            options.additional_context = this.build_confirmation_context(state);
            options.on_close = function(){
                self.getParent().getParent().reload.bind(self);

                // After action has been executed I have to check to see if the action has been canceled.
                // The only way that I know to do this is to read stage value from the server.
                // If the ID value of the clicked transition stage is the same as the value on the server
                // then the user has applied transition
                return rpc.query({
                    model: 'project.task',
                    method: 'read',
                    args: [self.res_id, ['stage_id']],
                }).then(function(record){
                    if (record[0].stage_id[0] == state.id)
                        self._update_state(state);
                });
            };
            return options;
        },

    });

    field_registry.add('task_workflow', TaskWorkflow);

    return TaskWorkflow;

});
