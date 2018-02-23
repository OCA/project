// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
odoo.define('project_workflow.workflow', function (require) {
'use strict';

var rpc = require('web.rpc');
require('web.dom_ready');
/*
 * This file is intended to add interactivity to task form rendered by
 * the website engine.
 */

var task_transition_buttons = $('.task-transition-button');

if(!task_transition_buttons.length) {
    return $.Deferred().reject("DOM doesn't contain project_portal_workflow elements");
}

task_transition_buttons.on('click',function(e){
    var $btn = $(this);
    $btn.prop('disabled', true);
    rpc.query({
            model: 'project.task',
            method: 'write',
            args: [[parseInt(e.currentTarget.getAttribute('task'), 10)],{
                stage_id: parseInt(e.currentTarget.getAttribute('data'), 10),
            },],
        })
        .fail(function() {
            $btn.prop('disabled', false);
        })
        .done(function () {
            window.location.reload();
        });
});


});
