/* Copyright 2018 Onestein
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('project_timeline_critical_path.backend', function (require) {
    'use strict';
    var TimelineRenderer = require('web_timeline.TimelineRenderer');

    TimelineRenderer.include({
        draw_critical_paths: function () {
            if (!this.critical_paths) {
                return;
            }

            var self = this;
            var paths = this.critical_paths;
            var items = this.timeline.itemSet.items;
            var task_ids = _.flatten(_.values(paths));
            var to_draw = [];
            _.each(items, function (item, item_id) {
                if (!item.data.evt) {
                    return;
                }
                _.each(item.data.evt[self.dependency_arrow], function (id) {
                    if (_.has(items, id)) {
                        if (_.contains(task_ids, id) &&
                            _.contains(task_ids, Number(item_id))) {
                            to_draw.push([item, items[id]]);
                        }
                    }
                });
            });

            _.each(to_draw, function (set) {
                self.draw_critical_path(set[0], set[1]);
            });
        },
        draw_critical_path: function (from, to) {
            if (!from.displayed || !to.displayed) {
                return;
            }

            this.canvas.draw_line(
                from.dom.box, to.dom.box,
                'red',
                2,
                false,
                10,
                12
            );
        },
        on_data_loaded_2: function (events) {
            var res = this._super.apply(this, arguments);
            if (this.modelName === 'project.task') {
                this.get_critical_paths(events).done(function (paths) {
                    this.critical_paths = paths;
                    this.draw_canvas();
                }.bind(this));
            }
            return res;
        },
        get_critical_paths: function (events) {
            var project_ids =
                _.uniq(
                    _.map(
                        _.filter(
                            events,
                            function (event) {
                                return event.project_id;
                            }
                        ),
                        function (event) {
                            return event.project_id[0];
                        }
                    )
                );

            return this._rpc({
                model: 'project.project',
                method: 'calc_critical_paths',
                args: [project_ids],
            });
        },
        draw_canvas: function () {
            var res = this._super.apply(this, arguments);
            this.draw_critical_paths();
            return res;
        },
    });
});
