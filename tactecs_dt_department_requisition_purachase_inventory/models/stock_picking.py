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
    is_requisition_return = fields.Boolean('is_requisition_return',store=True)
    breakdown_reason = fields.Char("سبب العطل",store=True)
    inventory_manager_approved = fields.Boolean("موافقة مدير المخزن ",store=True)
    writer_review = fields.Boolean("إطلاع كاتب الشطب ",store=True)

    check_committee_approved = fields.Boolean("موافقة لجنة الفحص",store=True)
    special_manager_approved = fields.Boolean("موافقة السلطة المختصه",store=True)
   

    requisition_number = fields.Char("رقم اذن الطلب",store=True)

    requisition_img = fields.Binary("صورة الطلب",store=True)
    requisition_img_name = fields.Char()


    def action_returns_committee_approval(self):
        for rec in self:
            if not rec.custody_state: 
                raise ValidationError("برجاء اضافة حالة المنتج")
            
            if rec.custody_state == 'fixable' and not rec.breakdown_reason:
                raise ValidationError("الرجاء كتابة سبب العطل ")
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

    def button_validate(self):
        for rec in self:

            if rec.picking_type_id.code =="incoming" :
                if not  rec.requisition_number or not rec.requisition_img :
                    raise ValidationError("الرجاء  ادخال صورة الطلب و رقم الطلب اولا")


            if rec.is_requisition_return  and not rec.inventory_manager_approved:
                raise ValidationError("لابد من  اتمام الموافقات المطلوبة اولا")

            else :
                return super(StockPicking, self).button_validate()



class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
