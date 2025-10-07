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
                    console.log(this._wysiwyg);
                });

            return Promise.all([def, loadProm]);
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onEditProfilePicClick: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget)
                .closest("form")
                .find(".o_forum_file_upload")
                .trigger("click");
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onFileUploadChange: function (ev) {
            if (!ev.currentTarget.files.length) {
                return;
            }
            var $form = $(ev.currentTarget).closest("form");
            var reader = new window.FileReader();
            reader.readAsDataURL(ev.currentTarget.files[0]);
            reader.onload = function (ev) {
                $form.find(".o_forum_avatar_img").attr("src", ev.target.result);
            };
            $form.find("#forum_clear_image").remove();
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onProfilePicClearClick: function (ev) {
            var $form = $(ev.currentTarget).closest("form");
            $form
                .find(".o_forum_avatar_img")
                .attr("src", "/web/static/src/img/placeholder.png");
            $form.append(
                $("<input/>", {
                    name: "clear_image",
                    id: "forum_clear_image",
                    type: "hidden",
                })
            );
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
