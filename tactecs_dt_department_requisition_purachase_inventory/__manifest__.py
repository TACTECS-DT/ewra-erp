# -*- coding: utf-8 -*-


{
    'name': 'TACTECS-DT Department Requisition from Purachase & Inventory',
    'version': '18.1',
    'summary': """TACTECS-DT Department Requisition from Purachase & Inventory""",
    'description': """    """,
    'author': 'TACTECS-DT',
    'website': 'http://www.tactecs-dt.com',
    'support': 'info@tactecs-dt.com',
    'images': ['static/description/img1.jpeg'],
    'category': 'Inventory/Inventory',
    'depends': [
                'stock',
                'hr',
                'purchase',
                'contacts',
                ],
    'data':[
        'security/security.xml',
        'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_requisition_sequence.xml',
        'data/employee_purchase_approval_template.xml',
        'data/confirm_template_material_purchase.xml',
        'report/purchase_requisition_report.xml',
        'views/requisition_view_employee.xml',
        'views/requisition_view_department_manager.xml',
        'views/requisition_view_inventory_manager.xml',
        'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/stock_picking_view.xml',
        'views/product.xml',
        'views/custody_manager_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
