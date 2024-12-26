# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import  ValidationError


# class HrEmployeePublic(models.Model):
#     _inherit = "hr.employee.public"

#     dest_location_id = fields.Many2one(
#         'stock.location',
#         string='Destination Location',
#     )

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        groups='hr.group_hr_user'
    )

    


    def action_view_employee_products_n(self):
        self.ensure_one()
        products = []
        return_products = []
        
        dest_location = self.dest_location_id.id if self.dest_location_id else False
    
  
        if not dest_location:
            raise ValidationError("You must set a destination location first") 
            



        domain = [("location_id","=",dest_location)]
        

     
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'res_model': 'stock.quant',
            'domain':domain,  
            'context': {'create': False,},
            'view_mode': 'list'
        }
    

    # def action_view_employee_products_n(self):
    #     self.ensure_one()
    #     products = []
    #     return_products = []
        
    #     dest_location = self.dest_location_id.id if self.dest_location_id else False
    
  
    #     if not dest_location:
    #         raise ValidationError("You must set a destination location first") 
            
              
    #     relate_picking =   self.env["stock.picking"].search([("location_dest_id","=",dest_location),("state","=",'done')])


    #     return_picking =   self.env["stock.picking"].search([("location_id","=",dest_location),("state","=",'done')])
        

        
    #     for i in return_picking :
    #         for line in i.move_ids_without_package :
    #             return_products.append(line.product_id.id)


        
    #     for i in relate_picking :
    #         for line in i.move_ids_without_package :
    #             p_id= line.product_id.id
    #             if p_id not in return_products :
    #                 products.append(p_id)





    #     domain = [('id', '=', products)]
        

     
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Products',
    #         'res_model': 'product.product',
    #         'domain':domain,  
    #         'context': {'create': False,},
    #         'view_mode': 'list'
    #     }
    
    
    # def action_view_employee_products_n(self):
    #     self.ensure_one()
    #     products = []
    #     return_products = []
        
    #     dest_location = self.dest_location_id.id if self.dest_location_id else False
        
    #     if not dest_location:
    #         raise ValidationError("You must set a destination location first") 
        
    #     relate_picking = self.env["stock.picking"].search([("location_dest_id", "=", dest_location), ("state", "=", 'done')])
    #     relate_return_picking = self.env["stock.picking"].search([("location_id", "=", dest_location), ("state", "=", 'done')])

    #     # Collect return quantities
    #     for r in relate_return_picking:
    #         for line in r.move_ids_without_package:
    #             return_products.append({"product_id": line.product_id.id, "qty": line.quantity})

    #     # Check quantities in relate_picking and whether they have been fully returned
    #     for i in relate_picking:
    #         for line in i.move_ids_without_package:
    #             pr_id = line.product_id.id
    #             qty_in_picking = line.quantity

    #             # Check if product has been returned or not
    #             qty_returned = sum([rp['qty'] for rp in return_products if rp['product_id'] == pr_id])

    #             remaining_qty = qty_in_picking - qty_returned

    #             if remaining_qty > 0:
    #                 products.append({"product_id": pr_id, "qty": remaining_qty})

    #     domain = [('id', 'in', [prod['product_id'] for prod in products])]
        
    #     print(relate_picking, "relate_picking") 
    #     print(products, "products") 
    #     print(domain, "domain") 

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Products',
    #         'res_model': 'product.product',
    #         'domain': domain,
    #         'context': {'create': False},
    #         'view_mode': 'list',
    #     }
