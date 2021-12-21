from odoo import fields, models, api


class ProductionLines (models.Model):
    _name = 'production.lines'
    _description = 'Modelo para almacenar las lineas de producción'

    name = fields.Char()
    code = fields.Char('Code')
    check_status = fields.Boolean('I.')



    


