# -*- coding: utf-8 -*-

import datetime
#from lxml import etree
from lxml import html
#import json
from dateutil.relativedelta import relativedelta
import requests
#import urllib

from odoo import api, fields, models
#from odoo.addons.web.controllers.main import xml2json_from_elementtree
from odoo.exceptions import UserError
#from odoo.tools.translate import _


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_interval_unit = fields.Selection([
        ('manually', 'Manualmente'),
        ('daily', 'Diario')],
        default='manually', string='Intervalo de Tiempo')
    currency_next_execution_date = fields.Date(string="Proxima Ejecucion")

    @api.multi
    def update_currency_rates(self):
        ''' This method is used to update all currencies given by the provider. Depending on the selection call _update_currency_ecb _update_currency_yahoo. '''
        res = True
        for company in self:
            res = company._update_currency()
            if not res:
                raise UserError('El servicio de Tipo de Cambio se encuentra fuera de linea. Cunsulte con su Administrador')

    def _update_currency(self):
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        currency = Currency.search([('name','=','USD')],limit=1)
        try:
            page = requests.get('http://www.sbs.gob.pe/app/xmltipocambio/TC_TI_Portal_xml.xml')
            tree = html.fromstring(page.content)
            dollar_rate = tree.xpath('//venta/text()')[0]
            dollar_rate = float(1) / float(dollar_rate)
        except:
            return False

        for company in self:
            if currency:
                CurrencyRate.create(
                    {'currency_id': currency.id, 'rate': dollar_rate, 'name': fields.Datetime.now(),
                     'company_id': company.id}
                )
        return True

    # def _update_currency_ecb(self):
    #     ''' This method is used to update the currencies by using ECB service provider.
    #         Rates are given against EURO
    #     '''
    #     Currency = self.env['res.currency']
    #     CurrencyRate = self.env['res.currency.rate']
    #
    #     currencies = Currency.search([])
    #     currencies = [x.name for x in currencies]
    #     request_url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    #     try:
    #         parse_url = requests.request('GET', request_url)
    #     except:
    #         #connection error, the request wasn't successful
    #         return False
    #     xmlstr = etree.fromstring(parse_url.content)
    #     data = xml2json_from_elementtree(xmlstr)
    #     node = data['children'][2]['children'][0]
    #     currency_node = [(x['attrs']['currency'], x['attrs']['rate']) for x in node['children'] if x['attrs']['currency'] in currencies]
    #     for company in self:
    #         base_currency_rate = 1
    #         if company.currency_id.name != 'EUR':
    #             #find today's rate for the base currency
    #             base_currency = company.currency_id.name
    #             base_currency_rates = [(x['attrs']['currency'], x['attrs']['rate']) for x in node['children'] if x['attrs']['currency'] == base_currency]
    #             base_currency_rate = len(base_currency_rates) and base_currency_rates[0][1] or 1
    #             currency_node += [('EUR', '1.0000')]
    #
    #         for currency_code, rate in currency_node:
    #             rate = float(rate) / float(base_currency_rate)
    #             currency = Currency.search([('name', '=', currency_code)], limit=1)
    #             if currency:
    #                 CurrencyRate.create({'currency_id': currency.id, 'rate': rate, 'name': fields.Datetime.now(), 'company_id': company.id})
    #     return True

    # def _update_currency_yahoo(self):
    #     ''' This method is used to update the currencies by using Yahoo service provider.
    #         Rates are given against the company currency, which will be also updated to a rate of 1
    #     '''
    #     Currency = self.env['res.currency']
    #     CurrencyRate = self.env['res.currency.rate']
    #     currencies = Currency.search([])
    #     for company in self:
    #         base_currency = company.currency_id.name
    #         currency_pairs = ','.join(base_currency + x.name for x in currencies if base_currency != x.name)
    #
    #         yql_base_url = "https://query.yahooapis.com/v1/public/yql"
    #         yql_query = 'select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20("' + currency_pairs + '")'
    #         yql_query_url = yql_base_url + "?q=" + yql_query + "&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
    #         try:
    #             url = urllib.urlopen(yql_query_url)
    #             result = url.read()
    #             url.close()
    #         except:
    #             #connection error, the request wasn't successful
    #             return False
    #         data = json.loads(result)
    #         if not data.get('query') or not data['query'].get('results'):
    #             #result is None, web service not available for the moment.
    #             return False
    #         #If we requested the rate for only one currency, the result is not a list. That happens if we
    #         #have only a foreign currency + the company one for example
    #         rates = len(currencies) < 3 and [data['query']['results']['rate']] or data['query']['results']['rate']
    #         for rate in rates:
    #             #If one of the currency asked is unrecognized: name will be 'N/A' and it must be ignored
    #             if rate['Name'] != 'N/A':
    #                 currency_code = rate['Name'].split('/')[-1]
    #                 currency = Currency.search([('name', '=', currency_code)], limit=1)
    #                 if currency:
    #                     CurrencyRate.create({'currency_id': currency.id, 'rate': rate['Rate'], 'name': fields.Datetime.now(), 'company_id': company.id})
    #         if company.currency_id.rate != 1.0:
    #             CurrencyRate.create({'currency_id': company.currency_id.id, 'rate': 1.0, 'name': fields.Datetime.now(), 'company_id': company.id})
    #     return True

    @api.model
    def run_update_currency(self):
        ''' This method is called from a cron job. Depending on the selection call _update_currency_ecb _update_currency_yahoo. '''
        records = self.search([('currency_next_execution_date', '<=', fields.Date.today())])
        if records:
            to_update = self.env['res.company']
            for record in records:
                if record.currency_interval_unit == 'daily':
                    next_update = relativedelta(days=+1)
                else:
                    record.currency_next_execution_date = False
                    continue
                record.currency_next_execution_date = datetime.datetime.now() + next_update
                to_update += record
            to_update.update_currency_rates()


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    currency_interval_unit = fields.Selection(related="company_id.currency_interval_unit",)
    currency_next_execution_date = fields.Date(related="company_id.currency_next_execution_date")

    @api.onchange('currency_interval_unit')
    def onchange_currency_interval_unit(self):
        if self.currency_interval_unit == 'daily':
            next_update = relativedelta(days=+1)
        else:
            self.currency_next_execution_date = False
            return
        self.currency_next_execution_date = datetime.datetime.now() + next_update

    @api.multi
    def update_currency_rates(self):
        companies = self.env['res.company'].browse([record.company_id.id for record in self])
        companies.update_currency_rates()
