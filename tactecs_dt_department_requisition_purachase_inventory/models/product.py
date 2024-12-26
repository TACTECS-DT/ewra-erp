    
from odoo import api, fields, models



class product_product(models.Model):
    _inherit  = 'product.product'
    
    # is_custody = fields.Boolean(string=' عهدة موظف ؟')
    custody_state = fields.Selection(selection=[("sustainable","مستديم"),("consumed","مستهلك")],string='حالة العهدة')


