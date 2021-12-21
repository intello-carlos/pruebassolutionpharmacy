# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

#Se actualiza la funcionalidad del boton confirmar, para que me genere una lista de materiales para un producto generico, dependiendo la cantidad de materias primas

    def action_confirm(self):
        raw = []
        values = []

        if self.order_line.product_id.name == 'Generico cotizador':
            for line in self.raw_material:
                dic = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                }
                raw.append((0,0,dic))
            values = {
                'product_tmpl_id': self.order_line.product_id.product_tmpl_id.id,
                'bom_line_ids': raw,
            }
            record_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.order_line.product_id.product_tmpl_id.id)])

            record = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.order_line.product_id.product_tmpl_id.id)]).bom_line_ids.bom_id
            delete = self.env['mrp.bom.line'].search([('bom_id', '=', record._origin.id)])
            delete.unlink()
            for record in record_ids:
                record.write(values)
            res = super(SaleOrder, self).action_confirm()
        else:
            res = super(SaleOrder, self).action_confirm()
        return res