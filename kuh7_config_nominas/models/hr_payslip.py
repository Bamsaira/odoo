# -*- coding: utf-8 -*-

import pytz
from datetime import date
from datetime import datetime, timedelta
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def validate_first_payroll_worker(self):
        v_fecha_ini_nomina = self.date_from.strftime('%Y-%m-%d')
        fecha_ini_nomina = datetime.strptime(v_fecha_ini_nomina, '%Y-%m-%d')

        v_fecha_fin_nomina = self.date_to.strftime('%Y-%m-%d')
        fecha_fin_nomina = datetime.strptime(v_fecha_fin_nomina, '%Y-%m-%d')

        v_fecha_ini_contrato = self.contract_id.date_start.strftime('%Y-%m-%d')
        fecha_ini_contrato = datetime.strptime(v_fecha_ini_contrato, '%Y-%m-%d')

        if fecha_ini_contrato >= fecha_ini_nomina and fecha_ini_contrato <= fecha_fin_nomina:
            self.first_payroll_worker = True
        else:
            self.first_payroll_worker = False

    first_payroll_worker = fields.Boolean(string="Primer Nómina Trabajador", help="Technical field for knowing if person is her first payslip", copy=False, default=False, compute="validate_first_payroll_worker")

