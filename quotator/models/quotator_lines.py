# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class QuotatorLine(models.Model):
    _name = "quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    quotator_id = fields.Many2one('quotator.own', string="Quotator id", store=True)
    category = fields.Char(string="Category", related="product_id.product_tmpl_id.categ_id.complete_name")
    material_qty = fields.Float(string="Quantity", default=1.0, digits='Product Unit of Measure', compute="_compute_qty", store=True)
    price_unit = fields.Float('Unit Price', required=True, default=0.0, compute="_update_price", store=True)
    price_total = fields.Float('Subtotal price', compute="_compute_price_total", store=True)
    sale_order = fields.Many2one('sale.order', 'Raw material', store=True)

    @api.depends('quotator_id.total_grams', 'percentage')
    def _compute_qty(self):
        for line in self:
            line.material_qty = (line.quotator_id.total_grams*line.percentage)/100
    
    @api.depends('quotator_id.partner_id.client_type', 'product_id')
    def _update_price(self):
        percentages = self.env['discount.rates'].search([('type_id.id', "=", self.quotator_id.partner_id.client_type.id)])
        for line in self:
            if not line.quotator_id.partner_id:
                raise ValidationError(_('!! You do not have, selected a client !!')) 
            else:
                if line.product_id:
                    price = line.quotator_id.partner_id.property_product_pricelist.get_product_price(line.product_id, 1.0 or line.material_qty, line.quotator_id.partner_id)
                    price = price+((price*percentages['percentage'])/100)
                    line['price_unit'] = 6 * price
    
    @api.depends('price_unit', 'material_qty')
    def _compute_price_total(self):
        for line in self:
            line['price_total'] = line['price_unit'] * line['material_qty']