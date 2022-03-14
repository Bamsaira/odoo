# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vender_por_peso = fields.Boolean(string='Por peso')
    peso = fields.Float(string='Peso (KG)')
    peso_producto = fields.Float(
        related='product_id.weight',
        string='Peso x UdM'
    )

    @api.onchange('vender_por_peso')
    def _onchange_vender_por_peso(self):
        self.product_uom_qty = 1
        self.product_uom = self.product_id.uom_id
        self.peso = 0

    @api.onchange('peso')
    def _onchange_peso(self):
        if self.vender_por_peso:
            if self.peso:
                self.product_uom_qty = self.peso / self.peso_producto
            else:
                self.product_uom_qty = 1

