# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        res = []
        for partner in self:
            if self.env.context.get('nombre_personalizado', False):
                name = partner.name
            else:
                name = partner._get_name()
            res.append((partner.id, name))
        return res