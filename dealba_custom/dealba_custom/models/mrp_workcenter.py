# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    secuencia_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Secuencia'
    )
    concatenar = fields.Boolean(string='Concatenar lotes')
