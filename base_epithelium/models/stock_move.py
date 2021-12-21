from odoo import fields, models, api
from odoo.tools import float_compare, float_is_zero, UserError
from collections import defaultdict


class StockMove(models.Model):
    _inherit = "stock.move"

    percent = fields.Float('Percent', digits='Precision Mrp')
    due_date = fields.Date('Due date')
    total = fields.Float('Total')
    product_uom_qty = fields.Float('Initial Demand', digits='Precision Mrp',
                                                     default=0.0, required=True, states={'done': [('readonly', True)]},
                                                     help="This is the quantity of products from an inventory "
                                                          "point of view. For moves in the state 'done', this is the "
                                                          "quantity of products that were actually moved. For other "
                                                          "moves, this is the quantity of product that is planned to "
                                                          "be moved. Lowering this quantity does not generate a "
                                                          "backorder. Changing this quantity on assigned moves affects "
                                                          "the product reservation, and should be done with care.")
    reserved_availability = fields.Float('Quantity Reserved', compute='_compute_reserved_availability',
                                                              digits='Precision Mrp',
                                                              readonly=True, help='Quantity that has already been reserved for this move')
    quantity_done = fields.Float('Quantity Done', compute='_quantity_done_compute', digits='Precision Mrp', inverse='_quantity_done_set')

    def _search_available_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None,
                                   owner_id=None, strict=True):
        """ Emule create of move lines.
        """
        self.ensure_one()

        if not lot_id:
            lot_id = self.env['stock.production.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']

        taken_quantity = min(available_quantity, need)

        # `taken_quantity` is in the quants unit of measure. There's a possibility that the move's
        # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
        # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
        # to convert `taken_quantity` to the move's unit of measure with a down rounding method and
        # then get it back in the quants unit of measure with an half-up rounding_method. This
        # way, we'll never reserve more than allowed. We do not apply this logic if
        # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
        # will take care of changing the UOM to the UOM of the product.
        if not strict:
            taken_quantity_move_uom = self.product_id.uom_id._compute_quantity(taken_quantity, self.product_uom,
                                                                               rounding_method='DOWN')
            taken_quantity = self.product_uom._compute_quantity(taken_quantity_move_uom, self.product_id.uom_id,
                                                                rounding_method='HALF-UP')

        quants = []

        if self.product_id.tracking == 'serial':
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
                taken_quantity = 0

        try:
            if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
                quants = self.env['stock.quant']._search_available_quantity(
                    self.product_id, location_id, taken_quantity, lot_id=lot_id,
                    package_id=package_id, owner_id=owner_id, strict=strict
                )
        except UserError:
            taken_quantity = 0

        # Find a candidate move line to update or create a new one.
        lots = []

        for available_quant, quantity in quants:
            if self.product_id.tracking == 'serial':
                for i in range(0, int(quantity)):
                    lots.append(self._prepare_move_line_vals(quantity=1, reserved_quant=available_quant))
            else:
                lots.append(self._prepare_move_line_vals(quantity=quantity, reserved_quant=available_quant))

        return lots
    
    def _create_quality_checks(self):
        # Used to avoid duplicated quality points
        quality_points_list = set([])

        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            pick_moves[move.picking_id] |= move

        for picking, moves in pick_moves.items():
            for check in picking.sudo().check_ids:
                point_key = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
                quality_points_list.add(point_key)
            quality_points = self.env['quality.point'].sudo().search([
                ('picking_type_id', '=', picking.picking_type_id.id),
                '|', ('product_id', 'in', moves.mapped('product_id').ids),
                '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
            for point in quality_points:
                if point.check_execute_now():
                    if point.product_id:
                        point_key = (picking.id, point.id, point.team_id.id, point.product_id.id)
                        if point_key in quality_points_list:
                            continue
                        self.env['quality.check'].sudo().create({
                            'picking_id': picking.id,
                            'point_id': point.id,
                            'team_id': point.team_id.id,
                            'product_id': point.product_id.id,
                            'company_id': picking.company_id.id,
                            'check_status': point.product_id.check_status,
                        })
                        quality_points_list.add(point_key)
                    else:
                        products = picking.move_lines.filtered(lambda move: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
                        for product in products:
                            point_key = (picking.id, point.id, point.team_id.id, product.id)
                            if point_key in quality_points_list:
                                continue
                            self.env['quality.check'].sudo().create({
                                'picking_id': picking.id,
                                'point_id': point.id,
                                'team_id': point.team_id.id,
                                'product_id': product.id,
                                'company_id': picking.company_id.id,
                                'check_status': point.product_id.check_status,
                            })
                            quality_points_list.add(point_key)
