/** @odoo-module **/

import {ProjectStateSelectionField} from "@project/components/project_state_selection/project_state_selection";
import {ProjectStatusWithColorSelectionField} from "@project/components/project_status_with_color_selection/project_status_with_color_selection_field";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

// Patch for project_state_selection widget (used in kanban and form views)
patch(
    ProjectStateSelectionField.prototype,
    "project_state_extend.project_state_selection",
    {
        /**
         * Override setup to initialize the service for custom colors
         */
        setup() {
            this._super(...arguments);
            this.projectStateExtend = useService("project_state_extend");
        },

        /**
         * Override to include custom status colors
         *
         * The options are already provided by the Python Selection field,
         * so we don't need to override get options(). We just need to
         * provide the colors for custom states.
         *
         * @param {String} value - The status value
         * @returns {String} The CSS class for the status color
         */
        statusColor(value) {
            // First try native colors
            const nativeColor = this._super(value);
            if (nativeColor) {
                return nativeColor;
            }

            // Then try custom colors
            if (this.projectStateExtend) {
                const customColors = this.projectStateExtend.getCustomStatusColors();

                if (customColors[value] !== undefined) {
                    const prefix =
                        this.colorPrefix || "o_status_bubble mx-0 o_color_bubble_";
                    return `${prefix}${customColors[value]}`;
                }
            }

            return "";
        },
    }
);

// Patch for status_with_color widget (used in tree/list views)
patch(
    ProjectStatusWithColorSelectionField.prototype,
    "project_state_extend.status_with_color",
    {
        /**
         * Override setup to initialize the service for custom colors
         */
        setup() {
            this._super(...arguments);
            this.projectStateExtend = useService("project_state_extend");
        },

        /**
         * Override to include custom status colors
         *
         * @param {String} value - The status value
         * @returns {String} The CSS class for the status color
         */
        statusColor(value) {
            // First try native colors using parent's logic
            if (this.colors && this.colors[value] !== undefined) {
                return this.colorPrefix + this.colors[value];
            }

            // Then try custom colors
            if (this.projectStateExtend) {
                const customColors = this.projectStateExtend.getCustomStatusColors();

                if (customColors[value] !== undefined) {
                    const prefix =
                        this.colorPrefix || "o_status_bubble mx-0 o_color_bubble_";
                    return `${prefix}${customColors[value]}`;
                }
            }

            return "";
        },
    }
);
