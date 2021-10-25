# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions, SUPERUSER_ID


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    alt_sequence = fields.Many2one('ir.sequence', string="Secuencia")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    stage_id = fields.Many2one('sale.order.stage', string='Stage', track_visibility='onchange', index=True, group_expand='_read_group_stage_ids')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # stage_ids = self.env['sale.order.stage'].search([])
        # return stage_ids

        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def create(self, vals):
        tid = self._context.get('default_team_id') or vals.get('team_id')
        if tid and vals.get('name', _('New')) == _('New'):
            team = self.env['crm.team'].search([('id', '=', tid)])
            sq = team.alt_sequence.code if team and team.alt_sequence and team.alt_sequence.code else 'sale.order'
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    sq) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(sq) or _('New')
        return super(SaleOrder, self).create(vals)
