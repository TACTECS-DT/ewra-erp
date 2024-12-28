from odoo import api, fields, models




class product_template(models.Model):
    _inherit  = 'product.template'
    
    custody_state = fields.Selection(selection=[("sustainable","مستديم"),("consumed","مستهلك")],string='حالة الصنف')





class product_product(models.Model):
    _inherit  = 'product.product'
    
    custody_state = fields.Selection(related='product_tmpl_id.custody_state',string='حالة الصنف',store=True)


