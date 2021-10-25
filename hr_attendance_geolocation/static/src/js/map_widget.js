odoo.define('hr_attendance_geolocation.location_map', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');

    var QWeb = core.qweb;

    var LocationMap = form_common.FormWidget.extend({
        view_type: "form",
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            this.display_result();
        },
        display_result: function () {
            this.$el.html(QWeb.render("WidgetCoordinates", {
                "coor_latitude": this.field_manager.get_field_value("latitude") || 0,
                "coor_longitude": this.field_manager.get_field_value("longitude") || 0,
            }));
        }
    });

    core.form_custom_registry.add('coordinates', LocationMap);
});