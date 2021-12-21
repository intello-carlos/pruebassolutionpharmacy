# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RestPartnerType(models.Model):
    _inherit = "res.partner"
    _description = "Add customer type field"

    client_type = fields.Many2one('type.client', string="Type client")

class TypeClient(models.Model):
    _name = 'type.client'
    _description = 'This module, contains the type of client'

    name = fields.Char(string='Name')
    code = fields.Integer()

    _sql_constraints = [
        ('name_uniq_client', 'UNIQUE(name)', '!No pueden existir dos tipos de clientes con el mismo nombre¡')
    ]

    @api.model
    def default_get(self, fields):
        res = super(TypeClient, self).default_get(fields)
        # Almacena el codigo por defecto al abrir la interfaz del modelo
        res.update({'code': len(self.env["type.client"].search([])) + 1})
        return res