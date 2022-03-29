# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _calculate_accumulated_month(self):
        total = 0
        if self.employee_id and self.contract_id.tablas_cfdi_id:
            if self.periodicidad_pago == '04':
                mes_actual = self.contract_id.tablas_cfdi_id.tabla_mensual.search(
                    [('mes', '=', self.mes), ('form_id', '=', self.contract_id.tablas_cfdi_id.id)], limit=1)
            else:
                mes_actual = self.contract_id.tablas_cfdi_id.tabla_semanal.search(
                    [('no_periodo', '=', self.no_periodo), ('form_id', '=', self.contract_id.tablas_cfdi_id.id)],
                    limit=1)

            date_start = mes_actual.dia_inicio  # self.date_from
            date_end = mes_actual.dia_fin  # self.date_to

            domain = [('state', '=', ['done', 'draft'])]
            if date_start:
                domain.append(('date_from', '>=', date_start))
            if date_end:
                domain.append(('date_to', '<=', date_end))

            domain.append(('employee_id', '=', self.employee_id.id))

            # if not self.contract_id.calc_isr_extra:
            domain.append(('tipo_nomina', '=', 'O'))

            rules = self.env['hr.salary.rule'].search([('code', '=', 'TPERG')])
            payslips = self.env['hr.payslip'].search(domain)
            payslip_lines = payslips.mapped('line_ids').filtered(lambda x: x.salary_rule_id.id in rules.ids)
            employees = {}
            for line in payslip_lines:
                if line.slip_id.employee_id not in employees:
                    employees[line.slip_id.employee_id] = {line.slip_id: []}
                if line.slip_id not in employees[line.slip_id.employee_id]:
                    employees[line.slip_id.employee_id].update({line.slip_id: []})
                employees[line.slip_id.employee_id][line.slip_id].append(line)

            for employee, payslips in employees.items():
                for payslip, lines in payslips.items():
                    for line in lines:
                        total += line.total
        # return total
        self.accumulated_taxable_perceptions = total
    
    def _calculate_accumulated_isr_sp_month(self):
        total = 0
        if self.employee_id and self.contract_id.tablas_cfdi_id:
            if self.periodicidad_pago == '04':
                mes_actual = self.contract_id.tablas_cfdi_id.tabla_mensual.search(
                    [('mes', '=', self.mes), ('form_id', '=', self.contract_id.tablas_cfdi_id.id)], limit=1)
            else:
                mes_actual = self.contract_id.tablas_cfdi_id.tabla_semanal.search(
                    [('no_periodo', '=', self.no_periodo), ('form_id', '=', self.contract_id.tablas_cfdi_id.id)],
                    limit=1)

            date_start = mes_actual.dia_inicio  # self.date_from
            date_end = mes_actual.dia_fin  # self.date_to

            domain = [('state', '=', ['done', 'draft'])]
            if date_start:
                domain.append(('date_from', '>=', date_start))
            if date_end:
                domain.append(('date_to', '<=', date_end))

            domain.append(('employee_id', '=', self.employee_id.id))

            # if not self.contract_id.calc_isr_extra:
            domain.append(('tipo_nomina', '=', 'O'))

            rules = self.env['hr.salary.rule'].search([('code', '=', 'ISR5')])
            payslips = self.env['hr.payslip'].search(domain)
            payslip_lines = payslips.mapped('line_ids').filtered(lambda x: x.salary_rule_id.id in rules.ids)
            employees = {}
            for line in payslip_lines:
                if line.slip_id.employee_id not in employees:
                    employees[line.slip_id.employee_id] = {line.slip_id: []}
                if line.slip_id not in employees[line.slip_id.employee_id]:
                    employees[line.slip_id.employee_id].update({line.slip_id: []})
                employees[line.slip_id.employee_id][line.slip_id].append(line)

            for employee, payslips in employees.items():
                for payslip, lines in payslips.items():
                    for line in lines:
                        total += line.total
        # return total
        self.accumulated_isr_sp = total

    accumulated_taxable_perceptions = fields.Float(string="Accumulated Taxable Perceptions", compute="_calculate_accumulated_month")
    accumulated_isr_sp = fields.Float(string="Accumulated ISR (SP)", compute="_calculate_accumulated_isr_sp_month")

