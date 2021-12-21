# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    raw_material = fields.One2many('raw.material', 'sale_order', string="Materials")
    medical_formula = fields.Binary('Medical formula', required=True)
    final_client = fields.Char(string="Final client")
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form")
    grams_pharmaceutical = fields.Float(string="Grams", digits='Product Unit of Measure')
    
class SaleOrderRaw(models.Model):
    _name = "raw.material"
    _description = "List of subjects"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    percentage = fields.Float(string="Percentage(%)")
    price_unit = fields.Float('Unit Price', digits='Product Unit of Measure')
    price_total = fields.Float('Subtotal price', digits='Product Unit of Measure')
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id", store=True)
    category = fields.Char(string="Category", related="product_id.categ_id.complete_name")
    sale_order = fields.Many2one('sale.order', 'Raw material')