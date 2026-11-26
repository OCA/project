odoo.define("portal.PortalProjectTaskCreate", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wysiwygLoader = require("web_editor.loader");

    publicWidget.registry.ProjectPortalTaskCreate = publicWidget.Widget.extend({
        selector: ".portal_task_crud",

        start: function () {
            var def = this._super.apply(this, arguments);

            var toolbar = [
                ["style", ["style"]],
                ["font", ["bold", "italic", "underline", "clear"]],
                ["para", ["ul", "ol", "paragraph"]],
                ["table", ["table"]],
                ["insert", ["link", "picture"]],
                ["history", ["undo", "redo"]],
            ];

            var $textarea = this.$("textarea.o_wysiwyg_loader");
            var loadProm = wysiwygLoader
                .loadFromTextarea(this, $textarea[0], {
                    toolbar: toolbar,
                    height: 350,
                    disableResizeImage: true,
                })
                .then((wysiwyg) => {
                    wysiwyg.toolbar.$el.find("#link, #media").remove();
                    this.$el
                        .find(".note-editable")
                        .find("img.float-start")
                        .removeClass("float-start");
                    this._wysiwyg = wysiwyg;
                    this._wysiwyg.$editable.addClass("bg-white p-2");
                });

            return Promise.all([def, loadProm]);
        },

        /**
         * @private
         */
        _onSubmitClick: function () {
            if (this._wysiwyg) {
                this._wysiwyg.save();
            }
        },
    });

    return publicWidget.registry.ProjectPortalTaskCreate;
});
