from odoo import models, fields, api


class PharmaceuticalForm(models.Model):
    _name = "pharmaceutical.form"
    _description = "Model that stores the dosage form"

    name = fields.Char(string="Compound")
    code = fields.Integer()

    @api.model
    def default_get(self, fields):
        res = super(PharmaceuticalForm, self).default_get(fields)
        # Almacena el codigo por defecto al abrir la interfaz del modelo
        res.update({'code': len(self.env["pharmaceutical.form"].search([])) + 1})
        return res


class PharmaceuticalPresentation(models.Model):
    _name = "pharmaceutical.presentation"
    _description = "Model that stores the type of presentation of a product"

    name = fields.Char(string="Presentation")
    code = fields.Integer()

    @api.model
    def default_get(self, fields):
        res = super(PharmaceuticalPresentation, self).default_get(fields)
        # Almacena el codigo por defecto al abrir la interfaz del modelo
        res.update({'code': len(self.env["pharmaceutical.presentation"].search([])) + 1})
        return res
