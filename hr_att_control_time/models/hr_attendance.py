# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    lunch_time = fields.Float(string='Refrigerio',
                              help='Esta cantidad de tiempo se descontara al tiempo total de trabajo, sólo si el tiempo de trabajo sobrepasa 4 horas')


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    chkin_time_diference = fields.Float('Entrada/Dif', compute="_compute_worked_hours", store=True, help='Se marca la diferencia de ingreso respecto al tiempo de trabajo')
    chkout_time_diference = fields.Float('Salida/Dif', compute="_compute_worked_hours", store=True, help='Se marca la diferencia de salida respecto al tiempo de trabajo')
    total_diference = fields.Float('Diferencia de turno', compute="_compute_worked_hours", store=True)
    department_id = fields.Many2one(store=True)

    def _get_resource_calendar_attendance(self, dt):
        resource_calendar_attendance = self.employee_id.calendar_id.attendance_ids.filtered(
            lambda x: x.dayofweek == str(dt.weekday()))
        return resource_calendar_attendance

    def _convert_float_to_time(self, date_float):
        hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(date_float * 60, 60))
        return timedelta(hours=int(hour[0:2]), minutes=int(hour[3:5]))

    def _get_time_from_datetime(self, dt):
        return timedelta(hours=dt.hour, minutes=dt.minute)

    # replace the method _compute_worked_hours to subtract at field worked_hours the lunch hours
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        super(HrAttendance, self)._compute_worked_hours()
        for attendance in self:
            if attendance.employee_id.calendar_id:
                dt_check_in = fields.Datetime.context_timestamp(self, timestamp=fields.Datetime.from_string(attendance.check_in))
                resource_calendar_attendance = attendance._get_resource_calendar_attendance(dt_check_in)

                if resource_calendar_attendance:
                    #if attendance.worked_hours >= 5:
                    attendance.worked_hours -= resource_calendar_attendance[0].lunch_time
                    attendance._compute_time_diference(resource_calendar_attendance[0])
                elif attendance.check_out:
                    attendance.chkout_time_diference = attendance.worked_hours
            if attendance.check_out:
                attendance.total_diference = attendance.chkin_time_diference + attendance.chkout_time_diference

    # compute time diference of checkin and checkout
    def _compute_time_diference(self, resource_calendar_attendance):
        hour_from = self._convert_float_to_time(resource_calendar_attendance.hour_from)
        check_in = self._get_time_from_datetime(
            fields.Datetime.context_timestamp(self, timestamp=fields.Datetime.from_string(self.check_in)))
        self.chkin_time_diference = (hour_from - check_in).total_seconds() / 3600.0

        if self.check_out:
            hour_to = self._convert_float_to_time(resource_calendar_attendance.hour_to)
            check_out = self._get_time_from_datetime(
                fields.Datetime.context_timestamp(self, timestamp=fields.Datetime.from_string(self.check_out)))
            self.chkout_time_diference = (check_out - hour_to).total_seconds() / 3600.0

    @api.model
    def run_attendance_chkout(self):
        attendance_ids = self.search([('check_out', '=', False)])
        for attendance in attendance_ids:
            employee_id = attendance.employee_id
            if employee_id.calendar_id:
                dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))
                hour_to = attendance._get_resource_calendar_attendance(dt).hour_to
                hour_to = divmod((hour_to - 2) * 60, 60)
                td_chkin = timedelta(hours=dt.hour,minutes=dt.minute)
                td_chkout = timedelta(hours=int(hour_to[0]),minutes=int(hour_to[1]))
                if td_chkin > td_chkout:
                    attendance.check_out = attendance.check_in
                else:
                    check_out = dt.replace(hour=int(hour_to[0]), minute=int(hour_to[1]), second=0)
                    attendance.check_out = fields.Datetime.to_string(
                        check_out.astimezone(pytz.utc))
            else:
                attendance.check_out = attendance.check_in

    @api.model
    def mark_attendances(self):
        date_start, date_end = self._get_current_datetime_zone()
        employees = self._get_employes_without_attendance(date_start, date_end)
        for employee in employees:
            attendance_time = self._get_time_attendance(employee, date_start)
            if attendance_time:
                hour_from = self._format_float_time(attendance_time[0].hour_from)
                hour_launch = self._format_float_time(attendance_time[0].lunch_time)
                dt_chkin = date_start.replace(hour=int(hour_from[0:2]), minute=int(hour_from[3:5]))
                if hour_launch:
                    dt_chkout = dt_chkin + timedelta(hours=int(hour_launch[0:2]),
                                                     minutes=int(hour_launch[3:5]))
                else:
                    dt_chkout = dt_chkin
                dt_chkin = fields.Datetime.to_string(dt_chkin.astimezone(pytz.utc))
                dt_chkout = fields.Datetime.to_string(dt_chkout.astimezone(pytz.utc))
                self.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': dt_chkin,
                    'check_out': dt_chkout,
                })

    def _get_current_datetime_zone(self):
        dt = fields.Datetime.context_timestamp(self, timestamp=datetime.now())
        return (dt.replace(hour=0, minute=0, second=0),
                dt.replace(hour=23, minute=59, second=59))
        # zone = pytz.timezone(self.env['res.users'].browse(SUPERUSER_ID).partner_id.tz)
        # return (datetime.now(zone).replace(hour=0, minute=0, second=0),
        #         datetime.now(zone).replace(hour=23, minute=59, second=59))

    def _get_employes_without_attendance(self, date_start, date_end):
        date_start_utc = fields.Datetime.to_string(date_start.astimezone(pytz.utc))
        date_end_utc = fields.Datetime.to_string(date_end.astimezone(pytz.utc))
        employes_with_attendance = self.env['hr.attendance'] \
            .search([('check_in', '>=', date_start_utc), ('check_in', '<=', date_end_utc)]).mapped('employee_id').ids
        return self.env['hr.employee'].search([('id', 'not in', employes_with_attendance)])

    def _get_time_attendance(self, employee, date):
        attendances = employee.calendar_id.attendance_ids.filtered(
            lambda x: x.dayofweek == str(date.weekday()))
        return attendances

    def _format_float_time(self, hour):
        if hour:
            return '{0:02.0f}:{1:02.0f}'.format(*divmod(hour * 60, 60))
        else:
            return False
