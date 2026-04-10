# -*- coding: utf-8 -*-
{
    'name': 'Invoice Metre Reading',
    'version': '17.0.0.1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Adding metre reading values to already exixting accounting module . The module works as an extension to the accounting module.',
    
    'description': """
        Odoo 17 Module: Invoice Metre Reading
        ======================================
        This module extends the Accounting module to add metre reading functionality to invoices.
        
        Features:
        ---------
        - Adds 'Previous Reading' column (auto-fetched from client's last posted invoice)
        - Adds 'New Reading' column (manual entry for current period)
        - Adds 'Actual Consumption' column (computed difference: New - Previous)
        - Automatically populates invoice line 'Quantity' with Actual Consumption
        - Fields are made  visible in form view, list view, and printed PDF reports
    """,
    'author': 'Joseph Gatuguta',
    'website': 'https://josephgatuguta.expert',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}