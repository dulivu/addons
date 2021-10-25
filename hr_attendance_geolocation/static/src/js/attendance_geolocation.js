odoo.define('hr_attendance_geolocation.attendance_geolocation', function (require) {
    "use strict";

    var Model = require('web.Model');
    var attendance = require('hr_attendance.my_attendances');

    attendance.include({
        /*init: function () {
            this._super.apply(this, arguments);
            var self = this,
                options = {enableHighAccuracy: true, timeout: 5000, maximumAge: 0};
            if ('geolocation' in navigator) {
                self.idWatchPosition = navigator.geolocation.watchPosition(
                    self.watchPosition.bind(self),
                    self.watchPositionError.bind(self),
                    options
                );
            } else {
                self.showAlert('¡Localizacion! ', 'Geolocalizacion no soportada', 'alert-warning');
            }
        },*/
        start: function () {
            this._super.apply(this, arguments);
            var self = this,
                options = {enableHighAccuracy: true, timeout: 5000, maximumAge: 0};
            if ('geolocation' in navigator) {
                self.idWatchPosition = navigator.geolocation.watchPosition(
                    self.watchPosition.bind(self),
                    self.watchPositionError.bind(self),
                    options
                );
            } else {
                self.showAlert('¡Localizacion! ', 'Geolocalizacion no soportada', 'alert-warning');
            }
        },
        destroy: function () {
            navigator.geolocation.clearWatch(this.idWatchPosition);
            Webcam.reset();
        },
        /* Mostrar alertas */
        showAlert: function (title, message, type) {
            var self = this,
                messageStructure = "<div class='alert " + type + " alert-dismissible' role='alert'>" +
                    "                   <button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>" +
                    "                   <strong>" + title + "</strong>" + message + "</div>";

            function timeToLoad() {
                setTimeout(function () {
                    if (self.$("#alert-message").length > 0) {
                        self.$("#alert-message").append(messageStructure);
                    } else {
                        timeToLoad();
                    }
                }, 200);
            }

            timeToLoad();
        },
        watchPositionError: function (err) {
            var title = '¡Localizacion! ';
            if (err.code == 1) {
                this.showAlert(title, 'Necesitamos permiso para detectar tu ubicacion', 'alert-warning');
            }
            if (err.code == 2) {
                this.showAlert(title, 'No se pudo acceder a su ubicacion', 'alert-warning');
            }
            if (err.code == 3) {
                this.showAlert(title, 'Tiempo de espera agotado', 'alert-warning');
            }
            if (typeof this.geolocation === "undefined")
                this.geolocation = false;
	    this.$(".o_hr_attendance_sign_in_out_icon").show();
        },
        watchPosition: function (location) {
            if (typeof this.geolocation !== "undefined" && this.geolocation !== false) {
                if (parseInt(location.coords.accuracy) < parseInt(this.geolocation.coords.accuracy)) {
                    this.geolocation = location;
                }
            }
            else {
                this.geolocation = location;
                this.$(".o_hr_attendance_sign_in_out_icon").show();
            }
            if (this.geolocation.coords.accuracy > 25) {
                this.$(".o_hr_attendance_sign_in_out_icon").removeClass("btn-primary").addClass("btn-warning");
            } else {
                this.$(".o_hr_attendance_sign_in_out_icon").removeClass("btn-warning").addClass("btn-primary");
            }
        },

        /* Llamar a la funcion attendance_manual de python para marcar la asistencia
         * @latitude: [string] latitud de la geolocalizacion
         * @longitude: [string] longitud de la geolocalizacion
         */
        markAttendance: function () {
            var self = this, latitude, longitude,
                hr_employee = new Model('hr.employee'),
                promesa = $.Deferred(),
                next_action = {
                    'type': 'ir.actions.act_url',
                    'url': '/',
                    "target": "self",
                };
            self.$('#text-loading').text('Guardando Posicion');
            if (self.geolocation) {
                latitude = self.geolocation.coords.latitude;
                longitude = self.geolocation.coords.longitude;
            }
            else {
                latitude = undefined;
                longitude = undefined;
            }
            hr_employee.call('attendance_manual',
                [[self.employee.id], next_action, undefined, latitude, longitude])
                .then(function (res) {
                    promesa.resolve(res);
                });
            return promesa.promise();
        },

        /* Guardar la foto tomada por la webcam|camara
         * @id_geolocation: [int] id del modelo a modificar
         * @data: [string] data de la foto a guardar
        */
        writePhoto: function (id_geolocation, data) {
            var self = this,
                hr_geolocation = new Model('hr.geolocation'),
                promesa = $.Deferred();
            self.$('#text-loading').text('Guardando Foto');
            hr_geolocation.call('write',
                [[id_geolocation], {photo: data}])
                .then(function (res) {
                    promesa.resolve(res);
                });
            return promesa.promise();
        },

        /* Tomar la foto utilizando la webcam|camara */
        takePhoto: function () {
            var promesa = $.Deferred();
            Webcam.snap(function (data_uri) {
                var data = data_uri.split(',')[1];
                promesa.resolve(data);
            }, function (err) {
                promesa.resolve(false);
            });
            return promesa.promise();
        },

        update_attendance: function () {
            var self = this;
            self.$('.loading').css({display: "flex"});
            $.when(self.takePhoto()).done(function (result1) {
                var idGeolocation = false;
                if (result1) {
                    self.markAttendance().then(function (result2) {
                        if (result2.action.attendance.check_out) {
                            idGeolocation = result2.action.attendance.chkout_location_id[0];
                        }
                        else {
                            idGeolocation = result2.action.attendance.chkin_location_id[0];
                        }
                        if (idGeolocation) {
                            self.writePhoto(idGeolocation, result1).then(function (res) {
                                self.$('.loading').css({display: "none"});
                                self.do_action(result2.action);
                            })
                        }
                    })
                }
                else {
                    self.showAlert('¡Asistencia! ', 'No pudimos capturar tu foto, por favor intentalo nuevamente', 'alert-warning');
                    self.$('.loading').css({display: "none"});
                }
            })
        },
    });

});
