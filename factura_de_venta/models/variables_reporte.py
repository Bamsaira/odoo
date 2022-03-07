# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
#Libreria para establecer una zona horaria
import pytz
#libreria para obtener datos de fecha y hora
import datetime
#libreria para convertir el numero a letra
from num2words import num2words


class ReportePersonalizado(models.Model):
    _inherit = 'account.move'

    #Creo funciones donde concentro la informacion de la compañia para luego mostrarlo.

    def _companyLetraMayuscula(self):
        company = self.company_id.name
        MAY_company = company.upper()
        return MAY_company

    def _direccion_company(self):
        direccion = self.company_id.street_name
        MAY_direccion = direccion.upper()
        return MAY_direccion

    def _direccion_company2(self):
        direccion3 = str(self.company_id.street_number) + ' ' + str(self.company_id.street2)
        MAY_direccion3 = direccion3.upper()
        return MAY_direccion3

    def _direccion2_company(self):
        direccion2 = str('C.P. ') + str(self.company_id.zip) + ' ' + str(self.company_id.city) + ', ' + str(self.company_id.state_id.name)
        MAY_direccion2 = direccion2.upper()
        return MAY_direccion2

    def _RFC_company(self):
        rfc = str('R.F.C.') + ' ' + str(self.company_id.vat)
        MAY_rfc = rfc.upper()
        return MAY_rfc

    def _telefono_company(self):
        telefono = str('+52 ') + ' ' + str(self.company_id.phone)
        MAY_telefono = telefono.upper()
        return MAY_telefono

    def _correo_company(self):
        correo = self.company_id.email
        return correo

    def _website_company(self):
        website = self.company_id.website
        return website

    def _company_register(self):
        register = self.company_id.company_registry
        return register

    # Se crea la funcion de convertir el numero a letra donde toma datos de la libreria agregada.

    def _total_en_letra(self):
        pre = float(self.amount_total)
        text = ''
        entire_num = int((str(pre).split('.'))[0])
        decimal_num = int((str(pre).split('.'))[1])
        if decimal_num < 10:
            decimal_num = decimal_num * 10
        text += num2words(entire_num, lang='es')
        text += ' punto '
        text += num2words(decimal_num, lang='es')
        return text.upper()

    #Defino una fecha y hora para obtener el valor en una variable y mostrarse en el documento.

    def _fecha_actual(self):
        tz = pytz.timezone('America/Mexico_City')
        ct = datetime.datetime.now(tz=tz)
        fecha_actual = ct.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual