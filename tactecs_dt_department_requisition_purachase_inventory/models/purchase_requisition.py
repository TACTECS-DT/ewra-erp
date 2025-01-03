# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import  UserError 
from odoo.exceptions import  ValidationError
class MaterialPurchaseRequisition(models.Model):
    
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']      # odoo11
    _order = 'id desc'
    
    #@api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
#                raise UserError(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()
    
    name = fields.Char(
        string='Number',
        index=True,
        readonly=1,
    )


    is_custody = fields.Boolean(string=' عهدة ؟')
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        # tracking=True,
        tracking=True
    )
    state_text = fields.Char(compute='get_current_stat_text',store=False,string='حالة الطلب ')
    request_date = fields.Date(
        string='Requisition Date',
        # default=fields.Date.today(),
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    refuse_reason = fields.Char(string=' سبب الرفض ',store=True)

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        readonly=True,
        copy=False,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager Reject',
        readonly=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rejected by',
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Purchase Requisitions Line',
        copy=True,
    )
    date_end = fields.Date(
        string='Requisition Deadline', 
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )
    date_done = fields.Date(
        string='Date Done', 
        readonly=True, 
        help='Date of Completion of Purchase Requisition',
    )
    managerapp_date = fields.Date(
        string='Department Approval Date',
        readonly=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Department Manager Reject Date',
        readonly=True,
    )
    userreject_date = fields.Date(
        string='Rejected Date',
        readonly=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    receive_date = fields.Date(
        string='Received Date',
        readonly=True,
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Requisitions',
        required=False,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible',
        copy=True,
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmed by',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )
    
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'custom_requisition_id',
        string='Purchase Ordes',
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )
    custody_return_requested = fields.Boolean(string="تم  طلب ارجاع العهدة",store=True)
        


    @api.onchange('requisition_line_ids')
    def check_is_custody(self):
        for rec in self:
            sustainable_product = rec.requisition_line_ids.filtered(
                lambda line: line.product_id.product_tmpl_id.custody_state == 'sustainable'
            )

            # If any sustainable product is found, set is_custody to True
            rec.is_custody = bool(sustainable_product)

    @api.constrains('requisition_line_ids')
    def _check_unique_product(self):
        for record in self:
            product_ids =  [ i.product_id.id for i in record.requisition_line_ids]
            if len(product_ids) != len(set(product_ids)):
                raise ValidationError("You cannot have duplicate products in the requisition lines.")
            


    def action_disbursed(self):
        
        stock_obj = self.env['stock.picking']

        for rec in self:
            # Search for the picking
            picking = stock_obj.search([
                ('custom_requisition_id', '=', rec.id),
                ('location_id', '=', rec.location_id.id),
                ('location_dest_id', '=', rec.dest_location_id.id)
            ])
            if len(picking) > 1:
                raise ValidationError('There is more than one picking to process.')
            if not picking:
                raise ValidationError('No picking found to process.')

            if picking.state not in ['confirmed', 'assigned']:
                picking.sudo().action_confirm()

            if picking.state not in ['confirmed', 'assigned']:
                raise ValidationError('The picking could not be confirmed.')

            move_lines = picking.move_ids_without_package
            requisition_lines = rec.requisition_line_ids

            self.cheack_line_products(requisition_lines)


            for requisition_line in requisition_lines:
                product = requisition_line.product_id
                qty_to_disburse = requisition_line.qty

                # Find matching stock move
                matching_move =  [ move  for move in move_lines if   move.product_id == product]
                print('matching_move',matching_move)
                print('matching_move',matching_move)
                if not matching_move or len(matching_move) == 0:
                    raise ValidationError(
                         f"No matching stock move found for product {product.display_name} with quantity {qty_to_disburse}."
                    )

                if len(matching_move) > 1:
                    raise ValidationError(
                        f"More than one matching stock move found for product {product.display_name}."
                    )

                # Update the stock move's quantity
                for move in matching_move:
                    if qty_to_disburse <= 0:
                        raise ValidationError(
                            f"Invalid quantity {qty_to_disburse} for product {product.display_name}."
                        )
                    move.product_uom_qty = qty_to_disburse
                    move.quantity = qty_to_disburse

            # Validate the picking after all moves are updated
            picking.button_validate()

            # Double-check the picking is done after validation
            if picking.state != 'done':
                raise ValidationError('The picking could not be validated successfully.')





    def cheack_line_products(self,requisition_lines):
        prs =[i.product_id for i in requisition_lines]
        if len(prs) != len(set(prs)):
            raise ValidationError('You cannot have duplicate products in the requisition lines.')




    def action_custody_return(self):
        for rec in self :
            stock_obj = self.env['stock.picking']
            move_obj = self.env['stock.move']
            picking_vals = {
                        'partner_id' : rec.employee_id.sudo().address_id.id if rec.employee_id.address_id else False,
               
                        'location_id' : rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                        'location_dest_id' : rec.location_id.id, 
                        'picking_type_id' : rec.custom_picking_type_id.id,
                        'note' : rec.reason,
                        'custom_requisition_id' : rec.id,
                        'is_requisition_return' : True,
                        'origin' : rec.name,
                        'company_id' : rec.company_id.id,
                    }
            stock_id = stock_obj.sudo().create(picking_vals)
            for line in rec.requisition_line_ids:
                if line.requisition_type =='internal':
                    pick_vals = rec._prepare_return_pick_vals(line, stock_id)
                    move_id = move_obj.sudo().create(pick_vals)

            rec.custody_return_requested =True

    
    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        vals.update({
            'name': name
            })
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res
        
    #@api.multi
    def requisition_confirm(self):
        for rec in self:
            manager_mail_template = self.env.ref('tactecs_dt_department_requisition_purachase_inventory.email_confirm_material_purchase_requistion')
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            if manager_mail_template:
                manager_mail_template.send_mail(self.id)
            
    @api.depends('state')
    @api.onchange('state')
    def get_current_stat_text(self):
        for rec in self :
            state_value = dict(self._fields['state'].selection).get(rec.state)
            rec.state_text = state_value
    # #@api.multi
    # def requisition_reject(self):
    #     for rec in self:
    #         if not rec.refuse_reason:
    #             raise ValidationError("الرجاء كتابة سبب الرفض")
    #         rec.state = 'reject'
    #         rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    #         rec.userreject_date = fields.Date.today()

    #@api.multi
    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            employee_mail_template = self.env.ref('tactecs_dt_department_requisition_purachase_inventory.email_purchase_requisition_iruser_custom')
            email_iruser_template = self.env.ref('tactecs_dt_department_requisition_purachase_inventory.email_purchase_requisition')
            # employee_mail_template.sudo().send_mail(self.id)
            # email_iruser_template.sudo().send_mail(self.id)
            employee_mail_template.send_mail(self.id)
            email_iruser_template.send_mail(self.id)
            rec.state = 'ir_approve'

    #@api.multi
    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    #@api.multi
    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'product_id' : line.product_id.id,
            'product_uom_qty' : line.qty,
            # 'quantity' : line.qty,

            'product_uom' : line.uom.id,
            'location_id' : self.location_id.id,
            'location_dest_id' : self.dest_location_id.id,
            'name' : line.product_id.name,
            'picking_type_id' : self.custom_picking_type_id.id,
            'picking_id' : stock_id.id,
            'custom_requisition_line_id' : line.id,
            'company_id' : line.requisition_id.company_id.id,
        }
        return pick_vals



    def _prepare_return_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'product_id' : line.product_id.id,
            'product_uom_qty' : line.qty,
            # 'quantity' : line.qty,
            'product_uom' : line.uom.id,
            'location_id' : self.dest_location_id.id,
            'location_dest_id' : self.location_id.id,
            'name' : line.product_id.name,
            'picking_type_id' : self.custom_picking_type_id.id,
            'picking_id' : stock_id.id,
            'custom_requisition_line_id' : line.id,
            'company_id' : line.requisition_id.company_id.id,
        }
        return pick_vals

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        seller = line.product_id._select_seller(
                partner_id=self._context.get('partner_id'), 
                quantity=line.qty,
                date=purchase_order.date_order and purchase_order.date_order.date(), 
                uom_id=line.uom
                )
        po_line_vals = {
                'product_id': line.product_id.id,
                'name':line.product_id.name,
                'product_qty': line.qty,
                'product_uom': line.uom.id,
                'date_planned': fields.Date.today(),
                 # 'price_unit': line.product_id.standard_price,
                'price_unit': seller.price or line.product_id.standard_price or 0.0,
                'order_id': purchase_order.id,
                 # 'account_analytic_id': self.analytic_account_id.id,
                'analytic_distribution':  {self.sudo().analytic_account_id.id: 100} if self.analytic_account_id else False,
                'custom_requisition_line_id': line.id
        }
        return po_line_vals
    
    #@api.multi
    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        #internal_obj = self.env['stock.picking.type'].search([('code','=', 'internal')], limit=1)
        #internal_obj = self.env['stock.location'].search([('usage','=', 'internal')], limit=1)
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
#         if not internal_obj:
#             raise UserError(_('Please Specified Internal Picking Type.'))
        for rec in self:
            if not rec.requisition_line_ids:
#                raise UserError(_('Please create some requisition lines.'))
                raise UserError(_('Please create some requisition lines.'))
            if any(line.requisition_type =='internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
#                        raise UserError(_('Select Source location under the picking details.'))
                    raise UserError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
#                        raise UserError(_('Select Picking Type under the picking details.'))
                    raise UserError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
#                    raise UserError(_('Select Destination location under the picking details.'))
                    raise UserError(_('Select Destination location under the picking details.'))
#                 if not rec.employee_id.dest_location_id.id or not rec.employee_id.department_id.dest_location_id.id:
#                     raise UserError(_('Select Destination location under the picking details.'))
                picking_vals = {
                        # 'partner_id' : rec.employee_id.sudo().address_home_id.id,
                        'partner_id' : rec.employee_id.sudo().address_id.id if rec.employee_id.address_id else False,
                        #'min_date' : fields.Date.today(),
                        'location_id' : rec.location_id.id,
                        'location_dest_id' : rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                        'picking_type_id' : rec.custom_picking_type_id.id,#internal_obj.id,
                        'note' : rec.reason,
                        'custom_requisition_id' : rec.id,
                        'origin' : rec.name,
                        'company_id' : rec.company_id.id,
                        
                    }
                stock_id = stock_obj.sudo().create(picking_vals)
                delivery_vals = {
                        'delivery_picking_id' : stock_id.id,
                    }
                rec.write(delivery_vals)
                
            po_dict = {}
            for line in rec.requisition_line_ids:
                if line.requisition_type =='internal':
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    move_id = move_obj.sudo().create(pick_vals)
                #else:
                if line.requisition_type == 'purchase': #10/12/2019
                    if not line.partner_id:
                        raise UserError(_('Please enter atleast one vendor on Requisition Lines for Requisition Action Purchase'))
#                        raise UserError(_('Please enter atleast one vendor on Requisition Lines for Requisition Action Purchase'))
                    for partner in line.partner_id:
                        if partner not in po_dict:
                            po_vals = {
                                'partner_id':partner.id,
                                'currency_id':rec.env.user.company_id.currency_id.id,
                                'date_order':fields.Date.today(),
#                                'company_id':rec.env.user.company_id.id,
                                'company_id':rec.company_id.id,
                                'custom_requisition_id':rec.id,
                                'origin': rec.name,
                            }
                            purchase_order = purchase_obj.create(po_vals)
                            po_dict.update({partner:purchase_order})
                            po_line_vals = rec.with_context(partner_id=partner)._prepare_po_line(line, purchase_order)
#                            {
#                                     'product_id': line.product_id.id,
#                                     'name':line.product_id.name,
#                                     'product_qty': line.qty,
#                                     'product_uom': line.uom.id,
#                                     'date_planned': fields.Date.today(),
#                                     'price_unit': line.product_id.lst_price,
#                                     'order_id': purchase_order.id,
#                                     'account_analytic_id': rec.analytic_account_id.id,
#                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                        else:
                            purchase_order = po_dict.get(partner)
                            po_line_vals = rec.with_context(partner_id=partner)._prepare_po_line(line, purchase_order)
#                            po_line_vals =  {
#                                 'product_id': line.product_id.id,
#                                 'name':line.product_id.name,
#                                 'product_qty': line.qty,
#                                 'product_uom': line.uom.id,
#                                 'date_planned': fields.Date.today(),
#                                 'price_unit': line.product_id.lst_price,
#                                 'order_id': purchase_order.id,
#                                 'account_analytic_id': rec.analytic_account_id.id,
#                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                rec.state = 'stock'
    
    #@api.multi
    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'
    
    #@api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id 

    #@api.multi
    def show_picking(self):
        #for rec in self:
            # res = self.env.ref('stock.action_picking_tree_all')
            # res = res.sudo().read()[0]
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        res['domain'] = str([('custom_requisition_id','=',self.id)])
        return res
        
    #@api.multi
    def action_show_po(self):
        # for rec in self:
        #     purchase_action = self.env.ref('purchase.purchase_rfq')
        #     purchase_action = purchase_action.sudo().read()[0]
        self.ensure_one()
        purchase_action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        purchase_action['domain'] = str([('custom_requisition_id','=',self.id)])
        return purchase_action
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
