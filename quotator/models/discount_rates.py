# -*- coding: utf-8 -*-

from typing import final
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class discount_rates(models.Model):
    _name = 'discount.rates'
    _description = 'This module, allows you to set the discount rates according to the client'
    _rec_name = 'type_id'

    type_id = fields.Many2one('type.client', string="Name")
    percentage = fields.Float(string="%")
    lines_price = fields.One2many('discount.rates.line', 'lines_id', string="Linea de precios")
    check_validation = fields.Boolean(string="Validation values", default=True)

    _sql_constraints = [
        ('type_client_uniq', 'UNIQUE(type_id)', '!No pueden existir dos tipos de clientes con las mismas tarifas¡')
    ]

    @api.constrains('lines_price')
    def _validation_values(self):
        for line in self.lines_price:
            if line.start >= line.final:
                raise ValidationError("!ERROR, el valor ingresado en los limites no es coherente¡")
    
    @api.constrains('check_validation')
    def _check_ok(self):
        if self.check_validation == False:
            raise ValidationError("!Por favor revisar los valores que se tiene alguna incoherencia¡")
    
    @api.onchange('lines_price')
    def _validation_range(self):
        datos = []
        i = -1
        for line in self.lines_price:
            items = ()
            items = items+(line.start, line.final)
            datos.append(items)
        
        for record in datos:
            i += 1
            values = datos
            values.pop(i)
            for vals in values:
                if record[0] in range(vals[0],vals[1]+1):
                    self.check_validation = False
                else:
                    self.check_validation = True
                if record[1] in range(vals[0],vals[1]+1):
                    self.check_validation = False
                else:
                    self.check_validation = True
                
    

class discount_rates_line(models.Model):
    _name = 'discount.rates.line'
    _description = 'This module contains the discount line'

    start = fields.Integer(string="Start")
    final = fields.Integer(string="Final")
    base_price = fields.Float(string="Base")
    lines_id = fields.Many2one('discount.rates', string="Base Price")
    
    