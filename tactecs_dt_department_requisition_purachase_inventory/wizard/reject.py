from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import  ValidationError

from odoo import api, Command, fields, models, tools,_

class Requisition_reject(models.TransientModel):
    _name = "wizard.requisition_reject"
    
    

    refuse_reason = fields.Char(string=' سبب الرفض ')

    
     
    def action_confirm (self):
        if not self.refuse_reason:
                raise ValidationError("الرجاء كتابة سبب الرفض")
        
        vals  = {
            "refuse_reason" : self.refuse_reason, 
            "state" : 'reject', 
            "userreject_date" : fields.Date.today(), 
            "reject_employee_id" : self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), 

         }
        active_id = self.env.context.get('active_id')
        requisition = self.env["material.purchase.requisition"].browse(active_id)
        requisition.write(vals)
  






