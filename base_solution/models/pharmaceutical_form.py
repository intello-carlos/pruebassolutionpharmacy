from odoo import models, fields, api

class PharmaceuticalForm(models.Model):
    _inherit = "pharmaceutical.form"

    value = fields.Float(string='Value x gr')

class PharmaceuticalPresentation(models.Model):
    _inherit = "pharmaceutical.presentation"

    value = fields.Float(string='Value x gr')