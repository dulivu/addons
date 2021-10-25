odoo.define('hr_attendance_geolocation.report_map', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');
    var Widget = require('web.Widget');
    var time = require('web.time');
    var translation = require('web.translation');

    var QWeb = core.qweb;
    var _t = translation._t;

    var ReportMap = Widget.extend({
        template: 'report_map',
        events: {
            'change input#date': 'changeDate',
            'click a.location': 'zoomMarker'
        },
        init: function (parent) {
            this._super(parent);
            var l10n = _t.database.parameters;
            this.date = moment().format('YYYY-MM-DD');
            this.date_format = time.strftime_to_moment_format(l10n.date_format);
            this.time_format = time.strftime_to_moment_format(l10n.time_format);
        },
        start: function () {
            var self = this;
            var start_day = moment().format('YYYY-MM-DD') + ' 00:00:00';
            var finish_day = moment().format('YYYY-MM-DD') + ' 23:59:59';
            start_day = time.auto_date_to_str(new Date(start_day),'datetime');
            finish_day = time.auto_date_to_str(new Date(finish_day),'datetime');
            $.when(self.getAttendances(start_day,finish_day))
                .done(function (res) {
                    self.attendances = res;
                    self.renderList();
                    self.renderMap();
                });
        },
        changeDate: function (e) {
            var self = this;
            var start_day = e.currentTarget.value + ' 00:00:00';
            var finish_day = e.currentTarget.value + ' 23:59:59';
            start_day = time.auto_date_to_str(new Date(start_day),'datetime');
            finish_day = time.auto_date_to_str(new Date(finish_day),'datetime');
            $.when(self.getAttendances(start_day,finish_day))
                .done(function (res) {
                    self.attendances = res;
                    self.renderList();
                    self.renderMap();
                });
        },
        getAttendances: function (start_day,finish_day) {
            var promesa = $.Deferred();
            var attendances = new Model('hr.attendance');
            attendances.query([])
                .filter([['check_in', '>=', start_day], ['check_in', '<=', finish_day]])
                .all().then(function (res) {
                if (res.length!=0){
                    promesa.resolve(res);
                }
                else {
                    promesa.resolve(false);
                }
            });
            return promesa.promise();
            /*attendances.query([])
                .filter([['check_in', '>=', start_day], ['check_in', '<=', finish_day]])
                .all().then(function (res) {
                self.attendances = res;
                if (self.attendances.length!=0){
                    self.formatData(res);
                    self.renderMap(res);

                }
                else {
                    self.$('.list-attendance').html("<div class='alert alert-info' role='alert'>" +
                        "No existe registros</div>");
                }
            });*/
        },
        renderList: function () {
            var self = this;
            if (self.attendances){
                var data = this.formatGetPhoto();
                //Agrupar asistencias por Empleado
                var attendances = [];
                var grouped = _.groupBy(data, 'employee_id');
                for (var i in grouped){
                    var array = [];
                    if (grouped.hasOwnProperty(i)){
                        array.push(i.split(',').slice(1));
                        array.push(grouped[i]);
                        attendances.push(array);
                    }
                }
                self.$('.list-attendance').html(QWeb.render("list_attendance",{widget:attendances}));
            }
            else {
                self.$('.list-attendance').html("<div class='alert alert-info' role='alert'>" +
                    "No existen registros</div>");
            }
        },
        formatGetPhoto: function () {
            var self = this;
            var attendances = self.attendances;
            for(var i=0;i<attendances.length;i++){
                var value1 = moment(time.auto_str_to_date(attendances[i].check_in));
                var value2 = moment(time.auto_str_to_date(attendances[i].check_out));
                attendances[i].chkin_display = value1.format(self.date_format+' '+self.time_format+' a');
                attendances[i].chkout_display = value2.format(self.date_format+' '+self.time_format+' a');
                if (attendances[i].chkin_location_id){
                    attendances[i].chkin_photo = "/web/image?model=hr.geolocation&id="+
                        attendances[i].chkin_location_id[0]+"&field=photo"
                }
                if(attendances[i].chkout_location_id){
                    attendances[i].chkout_photo = "/web/image?model=hr.geolocation&id="+
                        attendances[i].chkout_location_id[0]+"&field=photo"
                }
            }
            return attendances;
        },
        findEmployee: function (idEmployee) {
            var self = this;
            for (var i=0;i<self.attendances.length;i++){
                if (self.attendances[i].chkin_location_id[0] == idEmployee)
                    return self.attendances[i].employee_id[1];
                if (self.attendances[i].chkout_location_id[0] == idEmployee)
                    return self.attendances[i].employee_id[1];
            }
            return '';
        },
        renderMap: function () {
            var self = this;
            var location_ids = [];
            if (self.attendances){
                var attendances = self.attendances;
                for (var i = 0;i<attendances.length;i++){
                    if(attendances[i].chkin_location_id) location_ids.push(attendances[i].chkin_location_id[0]);
                    if(attendances[i].chkout_location_id) location_ids.push(attendances[i].chkout_location_id[0]);
                }
            }
            function loadMap() {
                setTimeout(function () {
                    if(typeof(google)!="undefined"){
                        var peru = {lat: -9.2155905, lng: -79.5149183};
                        self.map = new google.maps.Map(document.getElementById('map'), {
                            zoom: 6,
                            center: peru
                        });
                        if (location_ids.length != 0){
                            var locations = new Model('hr.geolocation');
                            locations.query(['latitude','longitude'])
                                .filter([['id','in',location_ids]])
                                .all().then(function (res) {
                                self.locations = res;
                                for (var i=0;i<res.length;i++)
                                     var marker = new google.maps.Marker({
                                         position: new google.maps.LatLng(parseFloat(res[i].latitude),parseFloat(res[i].longitude)),
                                         map: self.map,
                                         title: self.findEmployee(res[i].id)
                                     });
                                marker.setMap(self.map);
                            });
                        }
                    }else {
                        loadMap();
                    }
                },200);
            }
            loadMap();
        },
        zoomMarker: function (e) {
            var self = this;
            var location;
            var id = $(e.currentTarget).attr('data-chkin-location') || $(e.currentTarget).attr('data-chkout-location')
            for (var i=0;i<self.locations.length;i++){
                if(id==self.locations[i].id)
                    location = self.locations[i];
            }
            if(location){
                self.map.setZoom(18);
                self.map.setCenter({
                    lat: parseFloat(location.latitude),
                    lng: parseFloat(location.longitude)
                });
            }
        }
    });

    core.action_registry.add('hr_attendance_report_map', ReportMap);
    return ReportMap;
});