/** @odoo-module **/

import { Component, useState } from '@odoo/owl';

export class ProjectTimelineUserAvatar extends Component {
    setup() {
        this.state = useState({
            user_ids: this.props.user_ids || [],
        });
    }

    get avatarUrls() {
        return this.state.user_ids.map(user => {
            return {
                id: user.id,
                name: user.name,
                src: `/web/image/res.users/${user.id}/avatar_128/16x16`,
            };
        });
    }
}

ProjectTimelineUserAvatar.template = "project_timeline.UserAvatar";
