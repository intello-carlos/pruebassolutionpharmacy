from lxml import etree
from odoo import fields, models, api, _, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_production_line(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        if check_status:
            return self.env['production.lines'].search([('check_status', '=', check_status)], limit=1)
        else:
            return False

    production_line_id = fields.Many2one('production.lines', string='Production line', default=_default_production_line)
    check_status = fields.Boolean('I.', related='production_line_id.check_status', )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))

            seq_code = 'sale.order'
            if self.env['production.lines'].search([('id', '=', vals['production_line_id'])]).check_status:
                seq_code += '.i'

            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    seq_code, sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code, sequence_date=seq_date) or _('New')

        result = super(SaleOrder, self).create(vals)
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(SaleOrder, self).fields_view_get(view_id=view_id,
                                                     view_type=view_type,
                                                     toolbar=toolbar,
                                                     submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='production_line_id']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        res['arch'] = etree.tostring(doc)

        return res

    def _prepare_invoice(self):
        values = super(SaleOrder, self)._prepare_invoice()
        journal = self._journal_validate_invima()
        if not journal:
            raise exceptions.UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        values['journal_id'] = journal.id
        values['production_line_id'] = self.production_line_id

        return values

    def _journal_validate_invima(self):
        """
        Función que valida si la orden de venta es invima ya sea por una linea de producción o por una compra, de ser
        verdadero pone por defecto el primer diario en una busqueda del modelo account.journal .
        @author: Julián Valdés - Intello Idea
        """
        journal = None
        if self.check_status:
            option = self.env['account.journal'].search([('check_status', '=', True)])
            if option:
                journal = option[0]
        else:
            option = self.env['account.journal'].search([('check_status', '=', False)])
            if option:
                journal = option[0]

        return journal

    @api.onchange('production_line_id')
    def _clean_order_lines(self):
        if self.production_line_id:
            for line in self.order_line:
                if line.product_id.check_status != self.production_line_id.check_status:
                    self.order_line = None

    # def _create_invoices(self, grouped=False, final=False):
    #    invoice = super(SaleOrder, self)._create_invoices(grouped,final)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    check_status = fields.Boolean(related='order_id.check_status')


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
    check_status = fields.Boolean(related='order_id.check_status')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)

        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        invoice.check_status = check_status
        invoice.sale_check_status = check_status

        return invoice
