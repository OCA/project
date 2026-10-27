/** @odoo-module **/

import {ProjectTaskKanbanRenderer} from "@project/views/project_task_kanban/project_task_kanban_renderer";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {onWillStart} from "@odoo/owl";

patch(ProjectTaskKanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.isTemplateLinkedProject = false;
        onWillStart(async () => {
            const projectId = this.props.list.context.default_project_id;
            if (projectId) {
                const [project] = await this.orm.read(
                    "project.project",
                    [projectId],
                    ["template_id", "task_stage_order_enabled"]
                );
                this.isTemplateLinkedProject =
                    Boolean(project.template_id) && project.task_stage_order_enabled;
            }
        });
    },
    get canResequenceGroups() {
        return super.canResequenceGroups && !this.isTemplateLinkedProject;
    },
});
