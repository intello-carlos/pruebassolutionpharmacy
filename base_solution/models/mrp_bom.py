# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    pharmaceutical_id = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form")
    grams_pharmaceutical = fields.Float(string='Grams')
    
class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    percentage = fields.Float(string="Percentage")