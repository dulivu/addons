odoo.define('web.WebTreeDateName', function (require) {
    "use strict";
    var core = require('web.core');
    var list_widget_registry = core.list_widget_registry;

    var WebTreeImage = list_widget_registry.get('field').extend({
        format: function (row_data) {
            if (!row_data[this.id] || !row_data[this.id].value) {
                return '';
            }
            var name_day = moment.utc(row_data[this.id].value).local().format("dddd");
            return name_day;
        }
    });

    list_widget_registry
        .add('field.datename', WebTreeImage)
});