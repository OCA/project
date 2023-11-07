odoo.define("project_task_description_template.onchange_confirm_widget", function (
    require
) {
    "use strict";

    var field_registry = require("web.field_registry");
    var relational_fields = require("web.relational_fields");
    var FieldMany2One = relational_fields.FieldMany2One;

    var core = require("web.core");
    var Dialog = require("web.Dialog");

    var _t = core._t;

    var OnchangeConfirm = FieldMany2One.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        _change_template: function (ev) {
            this.trigger_up("field_changed", {
                dataPointID: ev.data.dataPointID,
                changes: ev.data.changes,
                skip: true,
            });
        },

        _onFieldChanged: function (ev) {
            var self = this;
            if (ev.data && !ev.data.skip) {
                ev.stopPropagation();
                var message = _t(
                    "The record has been modified, your changes will be discarded. Do you want to proceed?"
                );
                self.result = new Promise(function (resolve, reject) {
                    var dialog = Dialog.confirm(self, message, {
                        title: _t("Confirmation"),
                        confirm_callback: () => {
                            resolve(true);
                            self._change_template(ev);
                            self.result = undefined;
                        },
                        cancel_callback: () => {
                            reject(false);
                            self.result = undefined;
                        },
                    });
                    dialog.on("closed", self.result, reject);
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
    field_registry.add("onchange_confirm", OnchangeConfirm);
    return OnchangeConfirm;
});
