odoo.define('my_attendance_report.report', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');
    var time = require('web.time');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;

    var MyReport = Widget.extend({
        template: "MyAttendanceReport",
        init: function (parent) {
            this._super(parent);
            this.modeReport = 'weekly'; // modeReport options=['weekly','monthly'] default='weekly'
            this.currentDate = new moment();
            this.nowDate = new moment();
        },

        start: function () {
            var self = this;
            this.getEmployee(function () {
                self.renderHeader();
                self.renderListAttendances();
            });
            return this._super.apply(this, arguments);
        },

        /********************************
            RENDERIZACION DE LA VISTA
         ********************************/
        renderHeader: function () {
            var self = this;
            //self.getHeaderInfo().done(function () {
                var $header = self.$(".header").html(QWeb.render("MyAttHeader",
                    {
                        modeReport: self.modeReport,
                        currentDate: self.currentDate,
                        notWorkedDays: self.notWorkedDays,
                    }));
                $header.find('#weekly').bind('click', function (event) {
                    self.changeModeReport(event);
                });
                $header.find('#monthly').bind('click', function (event) {
                    self.changeModeReport(event);
                });
                $header.find('#prev-date').bind('click', function (event) {
                    self.changeDate(event);
                });
                $header.find('#next-date').bind('click', function (event) {
                    self.changeDate(event);
                });
                $header.find('#current-date').bind('click', function (event) {
                    self.changeDate(event);
                });
            //});
        },

        renderListAttendances: function () {
            var self = this;
            this.getlistAttendances(function (data) {
                self.$(".body").html(QWeb.render("listAttendances", {listAttendances: data}));
                /*var $body = self.$(".body").html(QWeb.render("listAttendances", {listAttendances: data}));
                $body.find(".board-attendance").bind('click', function (e) {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'hr.attendance',
                        res_id: parseInt(e.currentTarget.dataset.id),
                        view_mode: 'list,form',
                        views: [[false, 'form']],
                        target: 'new',
                        flags: {action_buttons: false, headless: false}
                    });
                })*/
            });
        },

        /*************************************
            FUNCIONES PRIVADAS DEL SERVIDOR
         *************************************/

        getHeaderInfo: function () {
            var self = this, deferred = $.Deferred();
            $.when(self.getNotWorkedDays()).done(function (res1) {
                self.notWorkedDays = res1;
                deferred.resolve();
            });
            return deferred.promise();
        },

        getDateStart: function () {
            if (this.modeReport == 'weekly') {
                return time.datetime_to_str(this.currentDate.startOf('week').toDate());
            }
            else {
                return time.datetime_to_str(this.currentDate.startOf('month').toDate());
            }
        },
        getDateFinish: function () {
            if (this.modeReport == 'weekly') {
                if (this.currentDate.format('W YYYY') === this.nowDate.format('W YYYY')) {
                    return time.datetime_to_str(this.nowDate.endOf('day').toDate());
                }
                return time.datetime_to_str(this.currentDate.endOf('week').toDate());
            }
            else {
                if (this.currentDate.format('M YYYY') === this.nowDate.format('M YYYY')) {
                    return time.datetime_to_str(this.nowDate.endOf('day').toDate());
                }
                return time.datetime_to_str(this.currentDate.endOf('month').toDate());
            }
        },
        applyChanges: function () {
            this.renderHeader();
            this.renderListAttendances();
        },

        /**************************
            CONSULTAS AL SERVIDOR
         **************************/
        getEmployee: function (callback) {
            var self = this, HrEmployee = new Model('hr.employee');
            HrEmployee.query(['name'])
                .filter([['user_id', '=', self.session.uid]])
                .all()
                .then(function (res) {
                    self.employee = res[0];
                    callback();
                })
        },
        getlistAttendances: function (callback) {
            var self = this, HrEmployee = new Model('hr.employee');
            HrEmployee.call('GetMyAttendances', [self.employee.id, self.getDateStart(), self.getDateFinish()]).then(function (result) {
                result = result[0];
                for (var i = 0; i < result.length; i++) {
                    result[i].check_in = moment(time.str_to_datetime(result[i].check_in));
                    result[i].check_out = result[i].check_out ? moment(time.str_to_datetime(result[i].check_out)) : false;
                }
                callback(result)
            });
        },

        getNotWorkedDays: function () {
            var self = this, HrEmployee = new Model('hr.employee'), deferred = $.Deferred();
            HrEmployee.call('get_days_not_worked', [self.employee.id, self.getDateStart(), self.getDateFinish()]).then(function (res) {
                deferred.resolve(res[0]);
            });
            return deferred.promise();
        },

        /**************************
            EVENTOS DE LA VISTA
         **************************/
        changeModeReport: function (e) {
            if (this.modeReport != e.currentTarget.id) {
                this.currentDate = new moment();
                if (e.currentTarget.id == 'monthly') {
                    this.modeReport = 'monthly';
                }
                else {
                    this.modeReport = 'weekly'
                }
                this.applyChanges();
            }
        },

        changeDate: function (e) {
            if (e.currentTarget.id == 'next-date' && this.modeReport == 'weekly') {
                this.currentDate.add(1, 'weeks');
            }
            if (e.currentTarget.id == 'next-date' && this.modeReport == 'monthly') {
                this.currentDate.add(1, 'months');
            }
            if (e.currentTarget.id == 'prev-date' && this.modeReport == 'weekly') {
                this.currentDate.subtract(1, 'weeks');
            }
            if (e.currentTarget.id == 'prev-date' && this.modeReport == 'monthly') {
                this.currentDate.subtract(1, 'months');
            }
            this.applyChanges();
        },
    });
    core.action_registry.add('my_attendance_report', MyReport);
    return MyReport;
});