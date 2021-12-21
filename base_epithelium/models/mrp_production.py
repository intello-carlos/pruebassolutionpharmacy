from odoo import fields, models, api, exceptions, _
from odoo.tools import float_compare, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
from lxml import etree


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_line_id = fields.Many2one('production.lines', related='bom_id.production_line_id',
                                         string='Production line')
    check_status = fields.Boolean('I.', related='product_id.check_status')
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', related='bom_id.pharmaceutical_form',
                                          string="Pharmaceutical form")
    pharmaceutical_presentation = fields.Many2one('pharmaceutical.presentation',
                                                  related='bom_id.pharmaceutical_presentation',
                                                  string="Pharmaceutical presentation")
    size = fields.Float(related='product_id.size', string="Size")
    partner_id = fields.Many2one('res.partner', string='Partner', )
    patient = fields.Char()
    due_date = fields.Date('Due date')

    lot_stock_move_line_ids = fields.One2many('stock.move.line', compute='_compute_lots', readonly=True, default=[],
                                              copy=False)
    mrp_production_simulation_lot_ids = fields.One2many(comodel_name='mrp.production.simulation.lot',
                                                        inverse_name='order_id',
                                                        default=[], copy=False)

    check_standard_manufacturing = fields.Boolean(related='product_id.standard_manufacturing')

    @api.onchange('product_id')
    def calculate_date_fin(self):
        if not self.product_id.standard_manufacturing:
            parameter = self.env['ir.config_parameter'].sudo()
            days_to_expiration = parameter.get_param('res.config.settings.days_to_expiration')

            expiration_date = date.today() + relativedelta(days=int(days_to_expiration))
            self.due_date = expiration_date

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            picking_type_id = values.get('picking_type_id') or self._get_default_picking_type()
            picking_type_id = self.env['stock.picking.type'].browse(picking_type_id)

            seq_code = 'mrp.production'
            if self.env['mrp.bom'].search([('id', '=', int(values['bom_id']))]).check_status:
                seq_code += '.i'

            if picking_type_id:
                values['name'] = picking_type_id.sequence_id.next_by_id()
            else:
                values['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')

            if values.get('origin') and not values.get('patient', False) and not values.get('partner_id', False):
                sale_order = self.env['sale.order'].search([('name', '=', values.get('origin'))])
                if sale_order:
                    sale_order_line = self.env['sale.order.line'].search(
                        [('order_id', '=', sale_order.id), ('product_id', '=', values.get('product_id'))], limit=1)
                    values['partner_id'] = sale_order.partner_id.id
                    if sale_order_line:
                        sale_order_patient_line = self.env['sale.order.line'].search(
                            [('order_id', '=', sale_order.id), ('display_type', '=', "line_note"),
                             ('sequence', '>=', sale_order_line.sequence)],
                            limit=1)
                        if sale_order_patient_line:
                            values['patient'] = sale_order_patient_line.name

        production = super(MrpProduction, self).create(values)
        return production

    @api.onchange('bom_id')
    def _get_picking_type(self):
        if self.bom_id:
            company_id = self.env.context.get('default_company_id', self.env.company.id)
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'mrp_operation'), ('warehouse_id.company_id', '=', company_id),
                 ('check_status', '=', self.check_status)], limit=1)
            if picking_type:
                self.picking_type_id = picking_type.id
            else:
                raise exceptions.ValidationError(_('Please create a picking type first'))

    def _get_move_raw_values(self, bom_line, line_data):
        data = super(MrpProduction, self)._get_move_raw_values(bom_line, line_data)
        data['percent'] = bom_line.percent
        return data

    @api.depends('move_raw_ids')
    def _compute_lots(self):
        for production in self:
            production.lot_stock_move_line_ids = []
            if production.move_raw_ids:
                for move in production.move_raw_ids:
                    move_line = production.env['stock.move.line'].search([('move_id', '=', move.id)])
                    production.lot_stock_move_line_ids += move_line

    def write(self, vals):
        return super(MrpProduction, self).write(vals)

    @api.depends('move_raw_ids')
    def action_emulate_move_lines(self):
        self.mrp_production_simulation_lot_ids = False
        for move in self.move_raw_ids:
            lots = []
            need_quantity = move.product_uom._compute_quantity(move.product_uom_qty,
                                                               move.product_id.uom_id,
                                                               rounding_method='HALF-UP')
            forced_package_id = move.package_level_id.package_id or None
            available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id,
                                                                                 package_id=forced_package_id)
            lots.extend(move._search_available_quantity(need_quantity, available_quantity, move.location_id,
                                                        package_id=forced_package_id, strict=False))
            for lot in lots:
                lot_obj = self.env['stock.production.lot'].search([('id', '=', lot['lot_id'])])
                cre = {
                    'order_id': self.id,
                    'product_id': lot['product_id'],
                    'quantity': lot['product_uom_qty'],
                    'lot': lot_obj.name if lot_obj else " ",
#Carlos                    'due_date': str(lot_obj.life_date) if lot_obj.life_date else " "
                }
                self.env['mrp.production.simulation.lot'].create(cre)

    @api.onchange('location_src_id', 'move_raw_ids', 'routing_id')
    def _onchange_location(self):
        super(MrpProduction, self)._onchange_location()
        self.action_emulate_move_lines()

    def get_composition_table(self):
        move_ids = self.move_raw_ids
        lot_ids = self.lot_stock_move_line_ids
        total_percent = 0
        total_quantity = 0
        total_quantity_lot = 0
        lines = []
        num = 0

        for move in move_ids:
            num += 1
            total_percent += move.percent
            total_quantity += move.product_uom_qty

            line = {
                'number': str(num),
                'product': str(move.product_id.name),
                'percent': str(move.percent),
                'quantity': str(move.product_uom_qty),
                'quantity_lot': "",
                'lot': "",
                'due_date': "",
                'head': True
            }
            lines.append(line)

            matches_lots = [lot for lot in lot_ids if lot['product_id'] == move.product_id]

            for lot_move in matches_lots:
                total_quantity_lot += lot_move.product_uom_qty if self.state in (
                    'confirmed') else lot_move.qty_done
                line = {
                    'number': "",
                    'product': "",
                    'percent': "",
                    'quantity': "",
                    'quantity_lot': str(lot_move.product_uom_qty) if self.state in ('confirmed') else lot_move.qty_done,
                    'lot': str(lot_move.lot_id.name),
                    'due_date': str(lot_move.due_date.strftime('%Y-%m-%d')) if lot_move.due_date else "",
                    'head': ""
                }
                lines.append(line)

            totals = {
                'total_percent': str(round(total_percent, 0)),
                'total_quantity': str(round(total_quantity, 0)),
                'total_quantity_lot': str(round(total_quantity_lot, 0))
            }

        return [lines, totals]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(MrpProduction, self).fields_view_get(view_id=view_id,
                                                         view_type=view_type,
                                                         toolbar=toolbar,
                                                         submenu=submenu)

        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_id']"):
            if check_status:
                node.set('domain', "[('check_status', '=', True)]")
            else:
                node.set('domain', "[]")

        res['arch'] = etree.tostring(doc)

        return res

    def plan_without_stock(self):
        bool = True
        for bom_obj in self.move_raw_ids:
            z = round(bom_obj.reserved_availability, 4)
            x = round(bom_obj.product_uom_qty, 4)
            if z == x:
                bool = False
            else:
                view = self.env.ref('base_epithelium.view_mrp_production_plan').id
                return {
                    'name': _('Activity to Manufacturing'),
                    'view_mode': 'form',
                    'view_id': view,
                    'res_model': 'wizard.mrp.production',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        if not bool:
            self.button_plan()
        else:
            view = self.env.ref('base_epithelium.view_mrp_production_plan').id
            return {
                'name': _('Activity to Manufacturing'),
                'view_mode': 'form',
                'view_id': view,
                'res_model': 'wizard.mrp.production',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
