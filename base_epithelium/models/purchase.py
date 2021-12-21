from lxml import etree
import json
from odoo import fields, models, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            parameter = self.env['ir.config_parameter'].sudo()
            check_status = parameter.get_param('res.config.settings.check_status')

            seq_date = None
            seq_code = 'purchase.order'
            if check_status or vals.get('check_status', False):
                seq_code += '.i'

            sequence = self.env['ir.sequence'].search([('code', '=', seq_code)])
            if not sequence:
                raise exceptions.UserError(_('The sequence ' + seq_code + 'not exist'))

            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self.env['ir.sequence'].next_by_code(seq_code, sequence_date=seq_date) or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='check_status']"):
            if check_status:
                node.set("readonly", "1")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
            else:
                node.set("readonly", "0")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = False
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc)

        return res

    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        result['context']['default_purchase_check_status'] = self.check_status
        return result

    @api.onchange('check_status')
    def _clean_order_lines(self):
        self.picking_type_id = None
        for line in self.order_line:
            if line.product_id.check_status != self.check_status:
                self.order_line = None


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    check_status = fields.Boolean(related='order_id.check_status')

    def report_compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])

            return taxes.get('taxes', [])
