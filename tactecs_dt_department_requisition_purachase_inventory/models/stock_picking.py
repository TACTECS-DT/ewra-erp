# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import  ValidationError 

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Purchase Requisition',
        readonly=True,
        copy=True
    )



    custody_state = fields.Selection(selection=[("new","جديد"),("used","مستعمل") ,("fixable","قابل للإصلاح"),("trash","كهنة او خردة")],string='حالة المنتج')

    returns_committee_approved = fields.Boolean("موافقة لجنة الإرتجاع",store=True)
    inventory_manager_approved = fields.Boolean("موافقة مدير المخزن ",store=True)
    writer_review = fields.Boolean("إطلاع كاتب الشطب ",store=True)

    check_committee_approved = fields.Boolean("موافقة لجنة الفحص",store=True)
    special_manager_approved = fields.Boolean("موافقة السلطة المختصه",store=True)


    def action_returns_committee_approval(self):
        for rec in self:
            if not rec.custody_state: 
                raise ValidationError("برجاء اضافة حالة المنتج")
            rec.returns_committee_approved =True
        return

    
    def action_inventory_manager_approval(self):
        for rec in self:
            rec.inventory_manager_approved =True
        return

    
    def action_writer_review(self):
        for rec in self:
            rec.writer_review =True
        return


    def action_check_committee_approved(self):
        for rec in self:
            rec.check_committee_approved =True
        return

    def action_special_manager_approved(self):
        for rec in self:
            rec.special_manager_approved =True
        return




class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
