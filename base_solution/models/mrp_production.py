# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    grams_pharmaceutical = fields.Float(String="Grams", digits='Product Unit of Measure', compute="_grams_pharmaceutical")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form", compute="_grams_pharmaceutical")
    order_line = fields.Integer(string="Order", store=True)

    @api.depends("origin")
    def _grams_pharmaceutical(self):
        result_query = self.env['sale.order.line'].search([('id', '=', self.order_line)])
        
        if result_query['pharmaceutical_form'] and result_query['grams_pharmaceutical']:
            self.pharmaceutical_form = result_query['pharmaceutical_form']
            self.grams_pharmaceutical = result_query['grams_pharmaceutical']
        else:
            self.pharmaceutical_form = self.bom_id.pharmaceutical_id.id
            self.grams_pharmaceutical = self.bom_id.grams_pharmaceutical

    @api.model
    def create(self, values):
        if values.get('origin'):
            sale_order = self.env['sale.order'].search([('name', '=', values.get('origin'))])
            if sale_order:
                sale_order_line = self.env['sale.order.line'].search(['&', ('order_id', '=', sale_order.id),
                                                                           ('product_id', '=', values.get('product_id')),
                                                                           ('product_uom_qty', '=', values.get('product_qty'))])
                values['order_line'] = sale_order_line['id']
        production = super(MrpProduction, self).create(values)
        return production