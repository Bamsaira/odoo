# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Variacion(models.Model):
    _name = "variacion"

    name = fields.Char(string='Variación')
    codigo = fields.Char(string='Código')
