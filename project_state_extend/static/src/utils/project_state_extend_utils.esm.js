/** @odoo-module **/

import {registry} from "@web/core/registry";

/**
 * Service to manage custom project states
 */
const projectStateCustomService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        const customStates = {};

        /**
         * Load custom states from database
         */
        async function loadCustomStates() {
            const states = await orm.searchRead(
                "project.state.extend",
                [["active", "=", true]],
                ["technical_name", "name", "color", "sequence"],
                {order: "sequence ASC"}
            );

            customStates.states = states;
            customStates.statusColors = {};

            // Build status colors mapping
            states.forEach((state) => {
                customStates.statusColors[state.technical_name] = state.color;
            });

            return customStates;
        }

        /**
         * Get all custom states (cached)
         *
         * @returns {Array} Array of custom state objects
         */
        function getCustomStates() {
            return customStates.states || [];
        }

        /**
         * Get custom status colors mapping
         *
         * @returns {Object} Object mapping technical_name to color index
         */
        function getCustomStatusColors() {
            return customStates.statusColors || {};
        }

        /**
         * Get merged status colors (native + custom)
         *
         * @param {Object} nativeStatusColors - Native status colors object
         * @returns {Object} Merged object with native and custom colors
         */
        function getMergedStatusColors(nativeStatusColors) {
            return {
                ...nativeStatusColors,
                ...getCustomStatusColors(),
            };
        }

        // Initialize on service start
        await loadCustomStates();

        return {
            loadCustomStates,
            getCustomStates,
            getCustomStatusColors,
            getMergedStatusColors,
        };
    },
};

registry.category("services").add("project_state_extend", projectStateCustomService);

export {projectStateCustomService};
