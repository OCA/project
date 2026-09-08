/** @odoo-module **/

import {KanbanModel} from "@web/views/kanban/kanban_model";
import {patch} from "@web/core/utils/patch";

const SUPPORTED_PROGRESSBAR_FIELDS = new Set(["last_update_status", "status"]);
const CUSTOM_PROGRESSBAR_PREFIX = "pstx";

function toCustomProgressBarClass(colorIndex) {
    return `${CUSTOM_PROGRESSBAR_PREFIX}-${colorIndex}`;
}

patch(KanbanModel.Group.prototype, "project_state_extend.kanban_progressbar", {
    _generateProgressBars() {
        const progressBars = this._super(...arguments);
        if (!this.model || !this.model.hasProgressBars) {
            return progressBars;
        }

        const {fieldName} = this.model.progressAttributes || {};
        if (!SUPPORTED_PROGRESSBAR_FIELDS.has(fieldName)) {
            return progressBars;
        }

        const fieldDefinition = this.fields && this.fields[fieldName];
        const fieldSelection = (fieldDefinition && fieldDefinition.selection) || [];
        if (!fieldSelection.length) {
            return progressBars;
        }

        const stateExtendService = this.model.env.services.project_state_extend;
        const customStatusColors = stateExtendService
            ? stateExtendService.getCustomStatusColors()
            : {};
        const existingValues = new Set(progressBars.map((bar) => bar.value));
        let insertAt = Math.max(progressBars.length - 1, 0);

        for (const [value, label] of fieldSelection) {
            if (existingValues.has(value)) {
                continue;
            }
            if (customStatusColors[value] === undefined) {
                continue;
            }
            progressBars.splice(insertAt, 0, {
                count: 0,
                value,
                string: label,
                color: toCustomProgressBarClass(customStatusColors[value]),
            });
            insertAt += 1;
            existingValues.add(value);
        }

        return progressBars;
    },
});
