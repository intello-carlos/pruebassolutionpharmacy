from odoo import fields, models, api
from lxml import etree
import json


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=_default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(AccountJournal, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
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


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                      string='Salesperson', default=lambda self: self.env.user)
                                      

    @api.onchange('partner_id')
    def charge_vendor(self):
        if self.partner_id:
            self.invoice_user_id = self.partner_id.user_id

    @api.model
    def _default_production_line(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        if check_status:
            return self.env['production.lines'].search([('check_status', '=', check_status)], limit=1)
        else:
            return False

    def default_purchase_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    production_line_id = fields.Many2one('production.lines', string='Production line', default=_default_production_line)
    sale_check_status = fields.Boolean('I.', related='production_line_id.check_status', readonly=False)
    purchase_check_status = fields.Boolean('I.', default=default_purchase_check_status)
    check_status = fields.Boolean(compute='_check_status_related', store=True)

    @api.onchange('production_line_id', 'purchase_check_status', 'sale_check_status')
    def _journal_validate_invima(self):
        """
        Función que valida si movimiento contable es invima ya sea por una linea de producción o por una compra, de ser
        verdadero agrega una tupla adicional al dominio del campo journal_id (diario) y pone por defecto el primer
        diario en una busqueda del modelo account.journal .
        @author: Julián Valdés - Intello Idea
        @return: Diccionario con una llave nombrada como el campo al cual se le quiere dar un dominio, como valor una
                 lista de tuplas
        """
        domain = {'journal_id': [('type', '=?', self.invoice_filter_type_domain)]}
        if self.type in ['out_invoice', 'out_refund', 'out_receipt']:
            if self.sale_check_status:
                domain['journal_id'].append(('check_status', '=', True))
                if not self.journal_id.check_status:
                    option = self.env['account.journal'].search(domain['journal_id'])
                    self.journal_id = None
                    if option:
                        self.journal_id = option[0].id
                return {'domain': domain}
            else:
                domain['journal_id'].append(('check_status', '=', False))
                if self.journal_id.check_status:
                    option = self.env['account.journal'].search(domain['journal_id'])
                    self.journal_id = None
                    if option:
                        self.journal_id = option[0].id
                return {'domain': domain}

        if self.type in ['in_invoice', 'in_refund', 'in_receipt']:
            if self.purchase_check_status:
                domain['journal_id'].append(('check_status', '=', True))
                if not self.journal_id.check_status:
                    option = self.env['account.journal'].search(domain['journal_id'])
                    self.journal_id = None
                    if option:
                        self.journal_id = option[0].id
                return {'domain': domain}
            else:
                domain['journal_id'].append(('check_status', '=', False))
                if self.journal_id.check_status:
                    option = self.env['account.journal'].search(domain['journal_id'])
                    self.journal_id = None
                    if option:
                        self.journal_id = option[0].id
                return {'domain': domain}

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        if self._context.get('default_type', False):
            parameter = self.env['ir.config_parameter'].sudo()
            check_status = parameter.get_param('res.config.settings.check_status')

            res = super(AccountMove, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)

            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='production_line_id']"):
                if check_status and (
                        self._context['default_type'] in ['out_refund', 'out_invoice', 'out_receipt', 'in_invoice',
                                                          'in_refund', 'in_receipt']):
                    node.set('domain', "[('check_status', '=', True)]")
                else:
                    node.set('domain', "[]")

            for node in doc.xpath("//field[@name='purchase_check_status']"):
                if check_status and (self._context['default_type'] in ['in_invoice', 'in_refund', 'in_receipt']):
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

        res = super(AccountMove, self).fields_view_get(view_id=view_id,
                                                       view_type=view_type,
                                                       toolbar=toolbar,
                                                       submenu=submenu)
        return res

    @api.depends('production_line_id', 'purchase_check_status', 'sale_check_status')
    @api.onchange('production_line_id', 'purchase_check_status', 'sale_check_status')
    def _check_status_related(self):
        """
        Funcion que valida los campos booleanos de sale_chech_status y purchase_check_status y dependiendo de que
        tipo de movimiento es iguale los valores al check status
        @author: Julián Valdés - Intello Idea
        """
        for account in self:
            if account.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                account.check_status = account.sale_check_status
            if account.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                account.check_status = account.purchase_check_status

    @api.onchange('check_status', 'purchase_check_status', 'sale_check_status')
    def _clean_order_lines(self):
        for line in self.invoice_line_ids:
            if line.product_id.check_status != self.check_status:
                self.invoice_line_ids = None


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    check_status = fields.Boolean(related='move_id.check_status')
