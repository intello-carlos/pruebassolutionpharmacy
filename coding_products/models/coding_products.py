# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo import exceptions
from odoo.tools.translate import *


class ProductGroup(models.Model):
    _name = "product.group"
    _description = "Products Group"

    name = fields.Char(string="Name Group", required=True)
    initials = fields.Char(string='Initials', required=True)
    consecutive = fields.Integer(string="Consecutive")
    range_zeros = fields.Integer(string='Range Zeros')
    is_automatic = fields.Boolean(string='Consecutive Automatic')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', "¡you cannot have records with the same name!"),
        ('initials_uniq', 'UNIQUE(initials)', "¡you cannot have records with the same initials!"),
        ('name_init_uniq', 'UNIQUE(name, initials)', "¡you cannot have records with the same names and initials!")
    ]

    @api.constrains('range_zeros')
    def _range_zeros(self):
        if self.range_zeros <= 0:
            raise exceptions.Warning(
                'El rango debe ser mayor que cero')
        else:
            print("ok")

    @api.model
    def create(self, vals):
        if vals["range_zeros"] <= 0:
            raise exceptions.Warning(
                'El rango debe ser mayor que cero')
        else:
            if vals.get('can_be_expensed', False):
                vals.update({'supplier_taxes_id': False})
            return super(ProductGroup, self).create(vals)


class Product(models.Model):
    _inherit = 'product.template'

    is_automatic = fields.Boolean(string='Consecutive Automatic', related='product_group.is_automatic')
    product_group = fields.Many2one("product.group", string='Product Group')

    _sql_constraints = [
        ('name_def_cod_uniq', 'UNIQUE(name, default_code, product_group)',
         "¡you cannot have records with the same names, default codes and product groups!"),
        ('name_cod_uniq', 'UNIQUE(name,product_group)',
         "¡you cannot have records with the same names and product groups!"),
        ('default_uniq', 'UNIQUE(default_code)', "¡you cannot have records with the same default codes!")
    ]

    @api.model
    def create(self, vals):
        prod_group = self.env['product.group'].search([("id", "=", vals["product_group"])])
        if not prod_group:
            raise exceptions.Warning('No ha seleccionado un Grupo de Producto válido')

        if len(str(prod_group.consecutive + 1)) > prod_group.range_zeros:
            raise exceptions.Warning('Los dígitos del consecutivo exceden el rango')
        else:
            zeros = prod_group.range_zeros - len(str(prod_group.consecutive + 1))
            # print(zeros)
            zerosl = ""
            for i in range(zeros):
                zerosl = zerosl + "0"
            # print(zerosl)
            if prod_group.is_automatic == True:
                vals["default_code"] = prod_group.initials + zerosl + str(prod_group.consecutive + 1)
            else:
                if not (vals["default_code"]):
                    raise exceptions.Warning(
                        'El Grupo de Producto, seleccionado no es automático, debe escribir la referencia')

            product = super(Product, self).create(vals)

            if product:
                if self._name == 'product.template':
                    prod_group.write({
                        "consecutive": prod_group.consecutive + 1
                    })

            return product

    @api.depends('product_group')
    def _compute_default_code(self):
        super(Product, self)._compute_default_code()
        for product in self:
            if not (product.id):
                if product.product_group:
                    if product.is_automatic:
                        # product_group = self.env['product.group'].search([("id", "=", product.product_group.id)])
                        if len(str(product.product_group.consecutive + 1)) <= product.product_group.range_zeros:
                            zeros = product.product_group.range_zeros - len(str(product.product_group.consecutive + 1))
                            print(zeros)
                            zerosl = ""
                            for i in range(zeros):
                                zerosl = zerosl + "0"
                            print(zerosl)
                            product.default_code = product.product_group.initials + zerosl + str(
                                product.product_group.consecutive + 1)
                        else:
                            product.default_code = "Los dígitos del consecutivo exceden el rango"


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _inherits = {'product.template': 'product_tmpl_id'}

    is_automatic = fields.Boolean(string='Consecutive Automatic', related='product_group.is_automatic')

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        prod_group = product.product_group

        if not prod_group:
            raise exceptions.Warning('No ha seleccionado un Grupo de Producto válido')

        if len(str(prod_group.consecutive + 1)) > prod_group.range_zeros:
            raise exceptions.Warning('Los dígitos del consecutivo exceden el rango')
        else:
            zeros = prod_group.range_zeros - len(str(prod_group.consecutive + 1))
            # print(zeros)
            zerosl = ""
            for i in range(zeros):
                zerosl = zerosl + "0"
            # print(zerosl)
            if prod_group.is_automatic == True:
                product.default_code = product.product_tmpl_id.default_code
                product.code = product.product_tmpl_id.default_code
            else:
                if not product.default_code:
                    raise exceptions.Warning(
                        'El Grupo de Producto, seleccionado no es automático, debe escribir la referencia')

            return product

    @api.onchange('product_group')
    def _compute_default_code(self):
        for product in self:
            if not (product.id):
                if product.product_group:
                    if product.is_automatic:
                        # product_group = self.env['product.group'].search([("id", "=", product.product_group.id)])
                        if len(str(product.product_group.consecutive + 1)) <= product.product_group.range_zeros:
                            zeros = product.product_group.range_zeros - len(str(product.product_group.consecutive + 1))
                            print(zeros)
                            zerosl = ""
                            for i in range(zeros):
                                zerosl = zerosl + "0"
                            print(zerosl)
                            product.default_code = product.product_group.initials + zerosl + str(
                                product.product_group.consecutive + 1)
                        else:
                            product.default_code = "Los dígitos del consecutivo exceden el rango"
