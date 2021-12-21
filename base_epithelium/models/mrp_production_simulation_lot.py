from odoo import fields, models, api


class MrpProductionSimulationLot(models.Model):
    _name = 'mrp.production.simulation.lot'
    _description = 'Model to store the simulation of batch consumption'

    order_id = fields.Many2one('mrp.production')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    lot = fields.Char(string='Lot')
    due_date = fields.Char()

