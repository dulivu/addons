# -*- coding: utf-8 -*-
import json
import werkzeug
from odoo import http
from odoo.http import request


class HrGeolocationPwa(http.Controller):

    @http.route('/mi_asistencia', auth='user')
    def myAsistencia(self, **kw):
        context = {
            'session_info': json.dumps(request.env['ir.http'].session_info())
        }
        return http.request.render('hr_attendance_geo.my-attendance', qcontext=context)

    @http.route('/sw-geolocation.js', type="http", auth="none", csrf=False)
    def load_worker(self, **kw):
        return http.Response('''

    var version = 'odoo-files-v1';
    var path = '/mi_asistencia';
    var path_mod = '/hr_attendance_geo'; 
    
    String.prototype.contains = function (search) {
        return this.indexOf(search) !== -1;
    }

    this.addEventListener('install', function (event) {
        event.waitUntil(
            caches.open(version).then(function (cache) {
                return cache.addAll([
                    new Request('.'+path, {credentials: 'include'}),
                    '.'+path_mod+'/static/src/css/bootstrap.min.css',
                    '.'+path_mod+'/static/src/css/estilos.css',
                    '.'+path_mod+'/static/src/css/font-awesome.min.css',

                    '.'+path_mod+'/static/src/js/angular.min.js',
                    '.'+path_mod+'/static/src/js/webcam.js',
                    '.'+path_mod+'/static/src/js/moment.js',
                    '.'+path_mod+'/static/src/js/main.js',

                    '.'+path_mod+'/static/src/fonts/FontAwesome.otf',
                    '.'+path_mod+'/static/src/fonts/fontawesome-webfont.eot',
                    '.'+path_mod+'/static/src/fonts/fontawesome-webfont.svg',
                    '.'+path_mod+'/static/src/fonts/fontawesome-webfont.ttf',
                    '.'+path_mod+'/static/src/fonts/fontawesome-webfont.woff',
                    '.'+path_mod+'/static/src/fonts/fontawesome-webfont.woff2',
                ]);
            }).then(function () {
                this.skipWaiting();
                console.log('sw: install completed');
            })
        );
    });

    this.addEventListener('fetch', function (event) {
        var rq = event.request;
        if (rq.method != 'GET') return;
        if (rq.url.contains('/web') && !rq.url.contains('/webcam.js')) return;
        
        if (!rq.referrer.contains(path)) {
            if (!rq.referrer) {
                if (!rq.url.contains(path)) return;
            }
            else {
                return;
            }
        }
        
        event.respondWith(
            caches.open(version).then(function(cache) {
                return cache.match(event.request).then(function (response) {
                    var fetchPromise = fetch(event.request).then(function(networkResponse) {
                        cache.put(event.request, networkResponse.clone());
                    });
                    return response || fetchPromise;
                });
            })
        );
    });

            ''', headers={
            'Content-type': 'application/javascript'
        })
