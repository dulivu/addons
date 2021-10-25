import pymssql
import pytz
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from zk import ZK, const


class HrAttendanceSummaryReport(models.AbstractModel):
    _name = 'report.hr_attendance_zkteco.template_report_attendance_summary'

    def _get_day(self, start_date, end_date):
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        for x in range(0, (end_date - start_date).days + 1):
            color = '#ababab' if start_date.strftime('%a') == 'Sat' or start_date.strftime('%a') == 'Sun' else ''
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day, 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res

    def _get_months(self, start_date, end_date):
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        while start_date <= end_date:
            last_date = start_date + relativedelta(day=1, months=+1, days=-1)
            if last_date > end_date:
                last_date = end_date
            month_days = (last_date - start_date).days + 1
            res.append({'month_name': start_date.strftime('%B'), 'days': month_days})
            start_date += relativedelta(day=1, months=+1)
        return res

    def _get_attendance_summary(self, start_date, end_date, empid):
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        for index in range(0, (end_date - start_date).days + 1):
            current = start_date + timedelta(index)
            res.append({'day': current.day, 'check_in': '', 'check_out': ''})
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', empid),
            ('check_in', '>=', str(start_date) + ' 00:00:00'),
            ('check_in', '<=', str(end_date) + ' 23:59:59')
        ])
        for att in attendances:
            # Convertir timezone de las marcaciones
            if att.check_out:
                check_in = fields.Datetime.from_string(att.check_in)
                check_in = fields.Datetime.context_timestamp(att, check_in)
                check_out = fields.Datetime.from_string(att.check_out)
                check_out = fields.Datetime.context_timestamp(att, check_out)
                res[(check_in.date() - start_date).days]['check_in'] = check_in.strftime('%H:%M')
                res[(check_in.date() - start_date).days]['check_out'] = check_out.strftime('%H:%M')
        return res

    def _get_data_from_report(self, data):
        res = []
        Employee = self.env['hr.employee']
        if 'depts' in data:
            for department in self.env['hr.department'].browse(data['depts']):
                res.append({'dept': department.name, 'data': [], 'color': self._get_day(data['date_from'], data['date_to'])})
                for emp in Employee.search([('department_id', '=', department.id)]):
                    res[len(res)-1]['data'].append({
                        'emp': emp.name,
                        'display': self._get_attendance_summary(data['date_from'], data['date_to'], emp.id),
                    })
        elif 'emp' in data:
            res.append({'data': []})
            for emp in Employee.browse(data['emp']):
                res[0]['data'].append({
                    'emp': emp.name,
                    'display': self._get_attendance_summary(data['date_from'], data['date_to'], emp.id),
                })
        return res

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        Report = self.env['report']
        attendance_report = Report._get_report_from_name('hr_attendance_zkteco.report_attendance_summary')
        attendance = self.env['hr.attendance'].browse(self.ids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': attendance_report.model,
            'docs': attendance,
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'get_day': self._get_day(data['form']['date_from'], data['form']['date_to']),
            'get_months': self._get_months(data['form']['date_from'], data['form']['date_to']),
            'get_data_from_report': self._get_data_from_report(data['form']),
        }
        return Report.render('hr_attendance_zkteco.template_report_attendance_summary', docargs)


class HrAttendancesSummary(models.TransientModel):
    _name = 'hr.attendance.summary.employee'
    _description = ''

    date_from = fields.Date(string='Desde', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    emp = fields.Many2many('hr.employee', 'summary_att_emp_rel', 'sum_id', 'emp_id', string='Employee(s)')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['emp'] = self.env.context.get('active_ids', [])
        employees = self.env['hr.employee'].browse(data['emp'])
        datas = {
            'ids': [],
            'model': 'hr.employee',
            'form': data
        }
        return self.env['report'].get_action(employees, 'hr_attendance_zkteco.template_report_attendance_summary', data=datas)


class HolidaysSummaryDept(models.TransientModel):

    _name = 'hr.attendance.summary.dept'

    date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    depts = fields.Many2many('hr.department', 'summary_att_dept_rel', 'sum_id', 'dept_id', string='Department(s)')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('depts'):
            raise UserError(_('Tiene que seleccionar por lo menos un departamento. Vuelva a intentarlo.'))
        departments = self.env['hr.department'].browse(data['depts'])
        datas = {
            'ids': [],
            'model': 'hr.department',
            'form': data
        }
        return self.env['report'].get_action(departments, 'hr_attendance_zkteco.template_report_attendance_summary', data=datas)


class HrAttendanceLoad(models.TransientModel):
    _name = 'hr.attendance.importzk'

    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    delete_onimport = fields.Boolean(string='Eliminar registros al importar', default=False)
    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='hr_employee_xw', string='Empleados')

    @api.multi
    def import_zkattendances(self):
        conn = pymssql.connect(server='192.168.1.18', user='interfase', password='ckantu', database='kantu_asistencia')
        for i in self:
            _from = i.date_from + ' 00:00:00'
            _to = i.date_to + ' 23:59:59'
            if i.employee_ids:
                ee_cursor = []
                for ee in i.employee_ids:
                    ee_cursor.append([ee.barcode])
            else:
                ee_cursor = conn.cursor()
                ee_cursor.execute("SELECT DISTINCT ui.badgenumber FROM [CHECKINOUT] ck "
                                  "INNER JOIN [userinfo] ui ON ck.[userid] = ui.[userid] "
                                  "WHERE checktime between '%s' and '%s'" % (_from, _to))

            for ee_row in ee_cursor:
                employee = self.env['hr.employee'].search([('barcode', '=', ee_row[0])])
                if employee:
                    if i.delete_onimport:
                        self.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            ('check_in', '>=', _from),
                            ('check_in', '<=', _to)
                        ]).unlink()

                    att_cursor = conn.cursor()
                    att_cursor.execute("SELECT DISTINCT ck.checktime, ck.checktype FROM [CHECKINOUT] ck "
                                       "INNER JOIN [userinfo] ui ON ck.[userid] = ui.[userid] "
                                       "WHERE checktime between '%s' and '%s' and ui.badgenumber = %s "
                                       "ORDER BY ck.checktime, ck.checktype" % (_from, _to, ee_row[0]))

                    data = {
                        'employee_id': employee.id,
                        'check_in': False,
                        'check_out': False
                    }
                    for att_row in att_cursor:
                        if not data['check_in']:
                            data['check_in'] = att_row[0]
                        elif not data['check_out']:
                            dt1 = data['check_in'].replace(hour=0, minute=0, second=0)
                            dt2 = att_row[0].replace(hour=0, minute=0, second=0)
                            if dt1 == dt2:
                                data['check_out'] = att_row[0]
                            else:
                                data['check_out'] = data['check_in']
                                data['check_in'] = pytz.timezone('America/Lima').localize(data['check_in']).astimezone(pytz.utc)
                                data['check_out'] = pytz.timezone('America/Lima').localize(data['check_out']).astimezone(pytz.utc)
                                self.env['hr.attendance'].create(data)
                                data['check_in'] = att_row[0]
                                data['check_out'] = False
                        else:
                            dt1 = data['check_out'].replace(hour=0, minute=0, second=0)
                            dt2 = att_row[0].replace(hour=0, minute=0, second=0)
                            if dt1 == dt2:
                                data['check_out'] = att_row[0]
                            else:
                                data['check_in'] = pytz.timezone('America/Lima').localize(data['check_in']).astimezone(pytz.utc)
                                data['check_out'] = pytz.timezone('America/Lima').localize(data['check_out']).astimezone(pytz.utc)
                                self.env['hr.attendance'].create(data)
                                data['check_in'] = att_row[0]
                                data['check_out'] = False

                    if data['check_in']:
                        if not data['check_out']:
                            data['check_out'] = data['check_in']
                        data['check_in'] = pytz.timezone('America/Lima').localize(data['check_in']).astimezone(pytz.utc)
                        data['check_out'] = pytz.timezone('America/Lima').localize(data['check_out']).astimezone(pytz.utc)
                        self.env['hr.attendance'].create(data)

        conn.close()
        return {}
