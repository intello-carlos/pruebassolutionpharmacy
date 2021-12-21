from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

#    due_date = fields.Datetime('Due Date', related="lot_id.life_date")
    due_date = fields.Datetime('Due Date')