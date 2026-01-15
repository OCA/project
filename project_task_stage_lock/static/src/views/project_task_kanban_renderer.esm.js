import {ProjectTaskKanbanRenderer} from "@project/views/project_task_kanban/project_task_kanban_renderer";
import {patch} from "@web/core/utils/patch";

patch(ProjectTaskKanbanRenderer.prototype, {
    get canResequenceGroups() {
        return false;
    },
});
